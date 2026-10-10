"""Generate a short actual simulator replay with Agg; opens no window or browser."""
import contextlib
import io
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "sim"))
import matplotlib
matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
from matplotlib.animation import PillowWriter
from sim.launch import make_sim
from sim.visualizer import draw
import rclpy_lite as rclpy


def main():
    out = ROOT / "demo"
    out.mkdir(exist_ok=True)
    sim = make_sim("goal-blocked", 0, False)
    fig, ax = plt.subplots(figsize=(6, 6.5))
    fig.suptitle("Autonomous core · clean-sensor simulation · 4× playback", fontsize=10)
    frames = []
    saved_stop = False
    writer = PillowWriter(fps=5)
    with contextlib.redirect_stdout(io.StringIO()), writer.saving(fig, str(out / "autonomous-demo.gif"), dpi=100):
        while not sim.done:
            for _ in range(4):
                if not sim.done:
                    sim.step()
            draw(ax, sim)
            fig.tight_layout(rect=(0, 0, 1, 0.96))
            writer.grab_frame()
            frames.append(dict(tick=sim.tick, simulated_seconds=sim.tick * 0.2,
                               result=sim.outcome, blocked=sim.rover.blocked_ticks,
                               replans=sim.score.replans, needless=sim.score.needless))
            if sim.score.events and sim.score.events[-1].kind == "stop" and not saved_stop:
                fig.savefig(out / "stopped.png", dpi=100)
                saved_stop = True
        fig.savefig(out / "final.png", dpi=100)
    plt.close(fig)
    (out / "frames.json").write_text(json.dumps(frames, indent=2))
    (out / "summary.txt").write_text(sim.summary() + "\n")
    rclpy.shutdown()
    print(f"Saved {len(frames)} actual simulator frames to {out}")


if __name__ == "__main__":
    main()
