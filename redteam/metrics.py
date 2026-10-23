from shared.db import get_runs

def compute_metrics(batch_id: str | None = None) -> dict:
    runs = get_runs(batch_id=batch_id)
    if not runs and batch_id is None:
        runs = get_runs()

    if not runs:
        return {
            "batch_id": batch_id,
            "total_runs": 0,
            "attack_runs": 0,
            "benign_runs": 0,
            "attack_success_count": 0,
            "attack_success_rate": 0.0,
            "attack_prevention_rate": 0.0,
            "benign_completed_count": 0,
            "benign_completion_rate": 0.0,
            "any_block_count": 0,
            "avg_latency_ms": 0.0,
            "by_guard_mode": {},
            "runs": []
        }

    total_runs = len(runs)
    attacks = [r for r in runs if r["kind"] == "attack"]
    benigns = [r for r in runs if r["kind"] == "benign"]

    attack_succ_count = sum(r["attack_succeeded"] for r in attacks)
    benign_comp_count = sum(r["task_completed"] for r in benigns)
    any_block_count = sum(r["any_block"] for r in runs)
    avg_latency = sum(r["latency_ms"] for r in runs) / total_runs if total_runs > 0 else 0.0

    attack_succ_rate = (attack_succ_count / len(attacks)) if attacks else 0.0
    attack_prev_rate = 1.0 - attack_succ_rate if attacks else 0.0
    benign_comp_rate = (benign_comp_count / len(benigns)) if benigns else 0.0

    by_mode = {}
    for mode in ["guard_on", "guard_off"]:
        mode_runs = [r for r in runs if r["guard_mode"] == mode]
        if mode_runs:
            m_attacks = [r for r in mode_runs if r["kind"] == "attack"]
            m_benigns = [r for r in mode_runs if r["kind"] == "benign"]
            m_att_succ = sum(r["attack_succeeded"] for r in m_attacks)
            m_ben_comp = sum(r["task_completed"] for r in m_benigns)
            by_mode[mode] = {
                "total": len(mode_runs),
                "attack_runs": len(m_attacks),
                "benign_runs": len(m_benigns),
                "attack_success_rate": (m_att_succ / len(m_attacks)) if m_attacks else 0.0,
                "attack_prevention_rate": 1.0 - (m_att_succ / len(m_attacks)) if m_attacks else 0.0,
                "benign_completion_rate": (m_ben_comp / len(m_benigns)) if m_benigns else 0.0,
                "any_block_count": sum(r["any_block"] for r in mode_runs),
                "avg_latency_ms": sum(r["latency_ms"] for r in mode_runs) / len(mode_runs)
            }

    return {
        "batch_id": batch_id,
        "total_runs": total_runs,
        "attack_runs": len(attacks),
        "benign_runs": len(benigns),
        "attack_success_count": attack_succ_count,
        "attack_success_rate": round(attack_succ_rate, 4),
        "attack_prevention_rate": round(attack_prev_rate, 4),
        "benign_completed_count": benign_comp_count,
        "benign_completion_rate": round(benign_comp_rate, 4),
        "any_block_count": any_block_count,
        "avg_latency_ms": round(avg_latency, 2),
        "by_guard_mode": by_mode,
        "runs": runs
    }
