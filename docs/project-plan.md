🗂️ **Project Plan – AI Traffic Light System (Full Project Roadmap)**
**🌟 Goal**
Design, build, and polish a full-stack AI-powered smart traffic light controller using YOLOv8, ByteTrack, and reinforcement learning (PPO/DQN), optimized for edge devices.

---

## ✅ Phase 0: Pre-Build Foundations (Planning Like a Pro)

### Step 1: Problem Definition

**Status:** ✅ Done
**Outputs:** `docs/problem-statement.md`

* **Problem:** Kenyan intersections rely on fixed-timer lights.
* **Users:** Nairobi traffic departments, rural municipalities.
* **Constraints:** No LIDAR, edge-only, no human override.
* **Success Metrics:** Reduced wait time, real-time decision making, 15+ FPS.

### Step 2: Research & Literature Review

**Status:** ✅ Done
**Outputs:** `docs/research-notes.md`

* YOLOv8 vs YOLOv5 vs YOLO-NAS
* RL in traffic systems (PPO > DQN)
* Failure cases, real deployments (Surtrac, Shenzhen)

### Step 3: System Architecture

**Status:** ✅ Done
**Outputs:** `docs/architecture.md`

* Module diagrams
* Real-time vs offline flows
* Swappable modules + future upgrades

### Step 4: Milestone Plan

**Status:** ✅ Done (this file)

* Weekly breakdown from training to deployment

### Step 5: Tooling & Setup

**Status:** ⏳ Partial

* `.gitignore`, `README.md`, `requirements.txt` ✅
* Dockerfile, Makefile, `setup.sh` ⏳
* GitHub repo structured and documented

---

## 🏠 Phase 1: Build Phase (Execution)

### Week 1: RL Environment

* Create `env.py`
* Define state/action/reward structure
* Add starvation penalty
* ✅ Test agent steps and reward returns

### Week 2: Simulation + PPO Training

* Connect `env.py` to Pygame sim
* Train agent with simulated data
* ✅ Watch reward curve improve, track decision patterns

### Week 3: Integrate Perception Stack

* Feed YOLOv8 + ByteTrack outputs into RL state
* ✅ Confirm real-time loop runs at 15+ FPS

### Week 4: End-to-End Loop Finalization

* RL agent controls live sim with visual feedback
* ✅ All lanes served, avoid starvation, log metrics

**Modules Involved:**

* `env.py`, `agent.py`, `sim.py`, `main.py`, `detector.py`, `tracker.py`, `counter.py`

---

## 🧪 Phase 2: Testing & Polish

### Stress Testing

* Run sim for 12h with randomized vehicle flow
* Introduce frame drops, corrupted inputs

### Error Handling

* Retry logic for YOLO errors
* Fallback to rule-based if RL fails
* Logging and FPS monitoring

**Test Suite:**

* `test_env.py`, `test_tracker.py`, `test_counter.py`
* Target: 80%+ test coverage with GitHub CI

---

## 🚢 Phase 3: Packaging & Deployment

### Dockerization

* `Dockerfile` using `python:3.10-slim`
* Maps video, logs folder
* CMD: `python main.py`

### Installer Scripts

* `setup.sh` for dependency check + folder creation
* `Makefile` for `make sim`, `make train`, `make eval`

### Delivery Targets

* Docker image ✅
* Offline-ready USB installer (RPi) ⏳

---

## 🧰 Phase 4: Evaluation

### Define Metrics

* Vehicles cleared/min
* Avg wait time/lane
* Starvation detection

### Controller Comparison

* Rule-based vs RL under identical load
* Plot results side-by-side using `matplotlib` or `plotly`

**Outputs:**

* `evaluation.md`, `comparison_plots.png`, `notebooks/eval_rules_vs_rl.ipynb`

---

## 🧠 Phase 5: Optional Enhancements

### Prediction Model

* Add LSTM to forecast 30s vehicle flow
* Feed prediction into RL state

### Anomaly Detection

* Detect jams, stuck cars
* Optional alert module

### Backend + Dashboard

* Log real-time stats to SQLite
* View insights via Streamlit or simple web dashboard

### Hardware Expansion

* Arduino or RPi control LEDs
* GPIO interface from RL agent
* Use real sensors for future validation

---

## 🚀 Phase 6: Deployment & Demo

### Documentation

* Full `README.md`
* Diagrams and explanations in `docs/`
* Dev guide in `docs/usage-guide.md`

### Walkthrough Demo

* Record screen + voiceover:

  * System overview
  * Real video → lights reacting
  * Explanation of decisions

### Reflection Post

* Write up lessons learned: reward shaping, sim challenges, YOLO tweaking
* Share on GitHub + LinkedIn

---

## 📂 Final Folder Structure (Condensed)

```
AI-TRAFFIC-LIGHT-SYSTEM/
├── core/
│   ├── perception/ (detector.py, tracker.py, counter.py)
│   ├── control/rl/ (env.py, agent.py, trainer.py)
│   ├── simulation/ (engine.py)
│   └── utils/ (logger.py, config_loader.py)
├── docs/
│   ├── problem-statement.md
│   ├── research-notes.md
│   ├── architecture.md
│   ├── project-plan.md
│   └── usage-guide.md
├── tools/ (zone_drawer.py, video_stabilizer.py)
├── tests/ (unit + integration tests)
├── deploy/ (Dockerfile, setup.sh, hardware/)
├── notebooks/ (rl_training.ipynb, analysis.ipynb)
├── .env.example
├── Makefile
├── README.md
└── requirements.txt
```

---

