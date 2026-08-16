import sqlite3
import pandas as pd

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from config import SNAPSHOTS, STATIC_FEATURES


# --- Encoding maps (dùng chung cho preprocessing pipeline) ---
DISAB_MAP = {'Y': 1, 'N': 0}

EDU_ORDER = {
    'No Formal quals':             0,
    'Lower Than A Level':          1,
    'A Level or Equivalent':       2,
    'HE Qualification':            3,
    'Post Graduate Qualification': 4,
}

# '10-20' (không có %) là cách ghi gốc trong OULAD
IMD_ORDER = {
    '0-10%': 0, '10-20': 1, '20-30%': 2, '30-40%': 3, '40-50%': 4,
    '50-60%': 5, '60-70%': 6, '70-80%': 7, '80-90%': 8, '90-100%': 9,
}


def build_snapshot_dataset(conn: sqlite3.Connection) -> pd.DataFrame:
    """Xây dựng dataset cho bài toán dự báo rủi ro học tập sớm.

    Với mỗi mốc thời gian T trong [30, 60, 90, 120, 150, 180, 210, 240] ngày,
    hàm tạo một snapshot thể hiện trạng thái của từng sinh viên tại thời điểm đó.

    Trước khi vào vòng lặp:
        - Join studentAssessment với assessments để lấy deadline, weight, loại bài thi.
        - Tính các cột phái sinh:
            - days_early: số ngày nộp sớm (âm = nộp trễ).
            - is_failed: 1 nếu điểm < 40, ngược lại 0.
            - weighted_score: điểm có trọng số = score × weight / 100.
            - Chuyển date_unregistration sang số để so sánh với T.

    Trong mỗi vòng lặp tại T:
        - Lọc sinh viên còn active: loại những sinh viên đã rút khỏi khoá trước ngày T.
        - VLE features (chỉ lấy dữ liệu đến tuần T // 7):
            - total_clicks: tổng số click tích luỹ đến T.
            - active_weeks: số tuần có tương tác.
            - avg_weekly_clicks: click trung bình mỗi tuần.
        - Assessment features (chỉ lấy bài có deadline <= T và đã nộp trước T):
            - num_submitted: số bài đã nộp.
            - avg_score: điểm trung bình có trọng số.
            - avg_days_early: độ trễ/sớm nộp bài trung bình.
            - num_failed: số bài bị trượt (< 40 điểm).
            - num_due được tính trong fill_in_assessment().
        - Static features: thông tin cá nhân sinh viên và nhãn final_result.
        - Merge tất cả lại, gắn prediction_point = T.

    Returns:
        DataFrame gồm 8 snapshot ghép lại — mỗi sinh viên xuất hiện tối đa 8 lần.
    """
    # --- Load tables ---
    student_info = pd.read_sql("SELECT * FROM studentInfo WHERE code_module != 'GGG'", conn)
    student_regs = pd.read_sql("SELECT * FROM studentRegistration", conn)

    student_regs['date_unregistration'] = pd.to_numeric(
        student_regs['date_unregistration'], errors='coerce'
    ).astype('float')

    # --- VLE: aggregate clicks per student per day (giữ "date" để lọc đúng T,
    # tránh lộ dữ liệu tương lai nếu gộp thẳng theo tuần rồi lọc theo week) ---
    vle_daily_agg = pd.read_sql("""
        SELECT
            id_student,
            code_module,
            code_presentation,
            date,
            SUM(sum_click) AS daily_clicks
        FROM studentVle
        GROUP BY id_student, code_module, code_presentation, date
    """, conn)

    # --- Assessment: join với assessments để lấy deadline và weight ---
    student_assessment_joined = pd.read_sql("""
        SELECT
            sa.id_student,
            sa.id_assessment,
            sa.date_submitted,
            sa.score,
            a.code_module,
            a.code_presentation,
            a.date   AS deadline_raw,
            a.weight
        FROM studentAssessment sa
        JOIN assessments a ON sa.id_assessment = a.id_assessment
        WHERE sa.is_banked = 0
          AND sa.score != '?'
    """, conn)

    student_assessment_joined['deadline'] = pd.to_numeric(
        student_assessment_joined['deadline_raw'], errors='coerce'
    ).astype('float')
    student_assessment_joined['score'] = pd.to_numeric(
        student_assessment_joined['score'], errors='coerce'
    ).astype('float')
    student_assessment_joined['days_early'] = (
        student_assessment_joined['deadline'] - student_assessment_joined['date_submitted']
    )
    student_assessment_joined['is_failed'] = (
        student_assessment_joined['score'] < 40
    ).astype(int)
    student_assessment_joined['weighted_score'] = (
        student_assessment_joined['score'] * student_assessment_joined['weight'] / 100
    )
    student_assessment_joined.drop(columns='deadline_raw', inplace=True)

    frames = []

    for T in SNAPSHOTS:
        # Chỉ giữ sinh viên còn active tại T
        active_students = student_regs[
            (student_regs['date_unregistration'].isna()) |
            (student_regs['date_unregistration'] > T)
        ]

        # VLE features — lọc đúng theo ngày trước, rồi mới quy ra tuần để đếm
        # active_weeks (tránh lộ dữ liệu của những ngày sau T trong cùng 1 tuần)
        vle_upto_T = vle_daily_agg[vle_daily_agg['date'] <= T].copy()
        vle_upto_T['week'] = vle_upto_T['date'] // 7
        vle_feat = (
            vle_upto_T
            .groupby(['id_student', 'code_module', 'code_presentation'])
            .agg(
                total_clicks = ('daily_clicks', 'sum'),
                active_weeks = ('week', 'nunique'),
            )
            .reset_index()
        )
        vle_feat['avg_weekly_clicks'] = vle_feat['total_clicks'] / vle_feat['active_weeks']

        # Assessment features — chỉ bài có deadline <= T và đã nộp trước T
        submitted_in_window = student_assessment_joined[
            (student_assessment_joined['deadline'] <= T) &
            (student_assessment_joined['date_submitted'] <= T)
        ]
        assess_feat = (
            submitted_in_window
            .groupby(['id_student', 'code_module', 'code_presentation'])
            .agg(
                num_submitted  = ('id_assessment', 'count'),
                total_w_score  = ('weighted_score', 'sum'),
                total_weight   = ('weight', 'sum'),
                avg_days_early = ('days_early', 'mean'),
                num_failed     = ('is_failed', 'sum'),
            )
            .reset_index()
        )
        assess_feat['avg_score'] = (
            assess_feat['total_w_score'] * 100 / assess_feat['total_weight'].replace(0, pd.NA)
        )
        assess_feat['avg_score'] = pd.to_numeric(assess_feat['avg_score'], errors='coerce').round(2)
        assess_feat['avg_days_early'] = assess_feat['avg_days_early'].round(2)
        assess_feat.drop(columns=['total_w_score', 'total_weight'], inplace=True)

        # Static features + label
        static = student_info[
            ['id_student', 'code_module', 'code_presentation'] + STATIC_FEATURES + ['final_result']
        ].merge(
            active_students,
            on=['id_student', 'code_module', 'code_presentation'],
            how='inner'
        )

        df_T = (
            static
            .merge(vle_feat,    on=['id_student', 'code_module', 'code_presentation'], how='left')
            .merge(assess_feat, on=['id_student', 'code_module', 'code_presentation'], how='left')
        )
        df_T['prediction_point'] = T
        frames.append(df_T)

    return pd.concat(frames, ignore_index=True)


def fill_in_weekly_clicks(df):
    df = df.copy()
    df['total_clicks_filled']      = df['total_clicks'].fillna(0)
    df['active_weeks_filled']      = df['active_weeks'].fillna(0)
    df['avg_weekly_clicks_filled'] = df['avg_weekly_clicks'].fillna(0)
    return df


def fill_in_assessment(df, assessment):
    df = df.copy()

    assessment_copy = assessment.copy()
    assessment_copy['date_num'] = pd.to_numeric(assessment_copy['date'], errors='coerce')

    num_due_frames = []
    for T in df['prediction_point'].unique():
        tmp = (
            assessment_copy[assessment_copy['date_num'] <= T]
            .groupby(['code_module', 'code_presentation'])
            .agg(num_due_true=('id_assessment', 'count'))
            .reset_index()
        )
        tmp['prediction_point'] = T
        num_due_frames.append(tmp)
    num_due_all = pd.concat(num_due_frames, ignore_index=True)

    df = df.merge(num_due_all, on=['code_module', 'code_presentation', 'prediction_point'], how='left')
    df['num_due'] = df['num_due_true'].fillna(0).astype(int)
    df.drop(columns='num_due_true', inplace=True)

    df['num_submitted_filled'] = df['num_submitted'].fillna(0).astype(int)
    df['num_failed_filled']    = df['num_failed'].fillna(0).astype(int)

    df['no_submission_despite_due'] = (
        (df['num_due'] > 0) & (df['num_submitted_filled'] == 0)
    ).astype(int)

    return df


def fit_imd_distributions(train_df):
    distributions = {}
    non_missing = train_df[train_df['imd_band'] != '?']
    for region, group in non_missing.groupby('region'):
        distributions[region] = group['imd_band'].value_counts(normalize=True)
    distributions['__overall__'] = non_missing['imd_band'].value_counts(normalize=True)
    return distributions


def transform_imd_imputation(df, distributions, rng):
    df = df.copy()
    student_key = ['id_student', 'code_module', 'code_presentation']

    # imd_band là static feature — impute 1 lần per student rồi broadcast về tất cả rows.
    # Không deduplicate thì cùng student nhận giá trị khác nhau ở mỗi snapshot.
    students = df[student_key + ['region', 'imd_band']].drop_duplicates(subset=student_key).copy()
    students['imd_band_filled'] = students['imd_band']

    for region, dist in distributions.items():
        if region == '__overall__':
            continue
        mask = (students['region'] == region) & (students['imd_band_filled'] == '?')
        if mask.sum() > 0:
            students.loc[mask, 'imd_band_filled'] = rng.choice(dist.index, size=mask.sum(), p=dist.values)

    still_missing = students['imd_band_filled'] == '?'
    if still_missing.any():
        overall = distributions['__overall__']
        students.loc[still_missing, 'imd_band_filled'] = rng.choice(
            overall.index, size=still_missing.sum(), p=overall.values
        )

    imputed = students[student_key + ['imd_band_filled']]
    df = df.merge(imputed, on=student_key, how='left')
    return df
