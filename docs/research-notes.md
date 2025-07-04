# Research Notes: AI Traffic Light Systems  
*Last Updated: July 2025*  

---

## 1. Core Technologies  

### Computer Vision for Traffic  
- **YOLOv8** outperforms older detectors (YOLOv7, Faster R-CNN) in speed/accuracy trade-off for edge devices  
  🔗 [Ultralytics Docs](https://docs.ultralytics.com/)  
- **ByteTrack** maintains 90%+ MOTA (Multi-Object Tracking Accuracy) even with occlusions  
  🔗 [arXiv:2110.06864](https://arxiv.org/abs/2110.06864)  

### Reinforcement Learning in Traffic Control  
- **PPO** is preferred over DQN for continuous action spaces like phase duration tuning  
  🔗 [OpenAI Spinning Up](https://spinningup.openai.com/)  
- **Reward Shaping**: Shenzhen’s RL-based system uses queue length + wait time penalties  
  🔗 [IEEE ITSC 2023](https://ieee-itss.org/)  

---

## 2. Existing Systems  

| System                | Approach               | Limitations                       | Source                                                                 |
|------------------------|------------------------|------------------------------------|------------------------------------------------------------------------|
| **Surtrac (Pittsburgh)** | RL + cameras           | Struggles with pedestrian priority | [CMU](https://www.cs.cmu.edu/surtrac/)                                |
| **Fraunhofer Lemgo**     | DNN + LiDAR            | High cost (~$8K per junction)      | [Fraunhofer](https://www.iosb.fraunhofer.de/en/traffic-optimization.html) |
| **Aston University**     | Edge-based YOLOv5      | Limited to 10 FPS on RPi           | [Aston](https://www.aston.ac.uk/traffic-ai)                           |

---

## 3. Key Findings  

1. **Edge Deployment Challenges**  
   - RPi 5 achieves ~14 FPS with YOLOv8n using INT8 quantization  
     🔗 [Seeed Studio Benchmark](https://www.seeedstudio.com/blog/2024/03/01/yolov8-on-raspberry-pi-5/)  

2. **RL Training Bottlenecks**  
   - Simulated environments (e.g., SUMO, Pygame) must maintain low latency (<100ms per step)  
     🔗 [SUMO-RL Paper](https://arxiv.org/abs/2103.16076)  

3. **Ethical Concerns**  
   - Camera-based vision raises privacy issues under the EU AI Act  
   - LiDAR anonymizes subjects better, reducing compliance risks  
     🔗 [EU AI Act 2025](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai)  

---

## 4. Open Problems  

- **Sim-to-Real Gap**: RL agents trained in simulation fail to generalize due to tracking noise, ID switches, and occlusions  
- **Multi-Modal Detection**: Hybrid models (YOLOv8 + Keypoint R-CNN) needed to accurately detect vehicles, bikes, and pedestrians simultaneously  

---

## 5. Recommended Reading  

1. 📘 [Adaptive Traffic Signals: A Survey (IEEE, 2024)](https://ieeexplore.ieee.org/document/10123456)  
2. ⚙️ [YOLOv8 for Edge Devices (Ultralytics, 2025)](https://ultralytics.com/yolov8)  
3. 🧠 [RL Reward Design for Traffic Control (NeurIPS 2024)](https://nips.cc/)  

---
