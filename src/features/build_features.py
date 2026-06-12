import sqlite3
import pandas as pd

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from config import SNAPSHOTS, STATIC_FEATURES


def build_snapshot_dataset(conn: sqlite3.Connection) -> pd.DataFrame:
    # --- Load tables ---
    student_info = pd.read_sql("SELECT * FROM studentInfo WHERE code_module != 'GGG'", conn)
    student_regs = pd.read_sql("SELECT * FROM studentRegistration", conn)

    student_regs['date_unregistration'] = pd.to_numeric(
        student_regs['date_unregistration'], errors='coerce'
    ).astype('float')

    # --- VLE: aggregate clicks per student per week ---
    vle_weekly_agg = pd.read_sql("""
        SELECT
            id_student,
            code_module,
            code_presentation,
            CAST(FLOOR(CAST(date AS FLOAT) / 7) AS INTEGER) AS week,
            SUM(sum_click) AS weekly_clicks
        FROM studentVle
        GROUP BY id_student, code_module, code_presentation, week
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

        # VLE features
        vle_feat = (
            vle_weekly_agg[vle_weekly_agg['week'] <= T // 7]
            .groupby(['id_student', 'code_module', 'code_presentation'])
            .agg(
                total_clicks = ('weekly_clicks', 'sum'),
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

        # num_due và submission_rate được tính trong fill_in_assessment (notebook),
        # nơi xử lý đúng cả sinh viên không nộp bài nào

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
    df[['total_clicks', 'active_weeks', 'avg_weekly_clicks']] = (
        df[['total_clicks', 'active_weeks', 'avg_weekly_clicks']].fillna(0)
    )
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

    df[['num_submitted', 'num_failed']] = (
        df[['num_submitted', 'num_failed']].fillna(0).astype(int)
    )

    df['submission_rate'] = df['num_submitted'] / df['num_due'].where(df['num_due'] > 0)

    df['no_submission_despite_due'] = (
        (df['num_due'] > 0) & (df['num_submitted'] == 0)
    ).astype(int)

    return df
