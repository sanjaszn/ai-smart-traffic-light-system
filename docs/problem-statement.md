# Problem Statement: AI‑Powered Adaptive Traffic Light Control System  

---

## 1. Core Problem  
Kenyan urban traffic control relies on outdated methods:

- **Fixed timers** that ignore real-time variability  
- **Inductive loops** that only detect metal, miss bikes/pedestrians, and cost $2K–$5K/junction  
- **Rule-based systems** that can’t adjust to emergencies or traffic surges  

These limitations lead to:

- 🚦 **Unnecessary congestion**, wasting millions of hours annually  
- 💸 **Economic loss**—Nairobi alone loses ~Kes 120 billion (~$1 billion) each year due to traffic jams :contentReference[oaicite:1]{index=1}  
- ⛽ **Fuel wastage and emissions**—Kenya loses ~Kes 50 million (~$350k) daily :contentReference[oaicite:2]{index=2}  
- 🏙 **Lower productivity**—Nairobi residents face ~57 minutes of commute daily, costing ~Kes 100 billion/year :contentReference[oaicite:3]{index=3}  

---

## 2. Proposed Solution  
An advanced **AI-driven traffic control system** that:

- Detects and tracks vehicles using **YOLOv8 + ByteTrack**—no need for embedded sensors  
- Utilizes **Reinforcement Learning** to optimize signal timing in response to live traffic data  
- Runs efficiently on **edge devices** (e.g., Raspberry Pi/Jetson), keeping costs below **$500/junction**

---

## 3. Stakeholders & Constraints  

| Stakeholder                 | Need                                           | Constraints & Goals                                           |
|----------------------------|------------------------------------------------|---------------------------------------------------------------|
| **City Traffic Authorities** | Reduce congestion without expensive overhauls | ≤ $500 hardware cost, ≥ 15 FPS edge inference performance      |
| **Commuters**              | Shorter, fair waits                            | ≤ 30 s lane starvation, pedestrian support in future phases   |
| **Environmental Agencies** | Lower emissions from idling traffic            | ≥ 20% reduction in idle time                                 |
| **Emergency Services**     | Timely passage through intersections           | ≥ 95% green-wave success for emergency scenarios             |

---

## 4. Success Metrics  

| Metric                          | Static Baseline             | AI System Target           | Measurement Approach                         |
|--------------------------------|-----------------------------|----------------------------|----------------------------------------------|
| Avg. wait time/vehicle        | ~45 s                      | ≤ 30 s                     | Sim logs vs. real-time performance           |
| Vehicles cleared per minute   | 12–15                      | ≥ 20                       | Zone-counter outputs                         |
| Junction hardware cost        | ~$2K                       | ≤ $500                     | BOM analysis                                 |
| Idle-time emissions/fuel      | —                          | ≥ 20% reduction            | Simulated CO₂/fuel consumption models        |
| Daily economic cost           | Kes 100–120 billion/year   | Significantly reduced      | Economic modeling & commuter surveys         |

---

## 5. Technical Challenges  

1. **Low latency demand**: RL controller must respond within 100 ms  
2. **Sim-to-real drift**: Real-world tracking may suffer occlusions or ID swaps  
3. **Fairness constraints**: Reward shaping to avoid lane starvation while boosting flow  
4. **Multi-modal detection**: Future rollout of cyclist/pedestrian-aware models

---

## 6. Ethical & Safety Considerations  

- **Privacy**: Option for LiDAR-based anonymization in place of cameras for sensitive detection  
- **Manual override**: Support traffic officer intervention and emergency signals  
- **Safety enforcement**: Use action masking to prevent unsafe signal changes

---

## 7. Key Insights & Citations  

- **Kes 120 billion/year lost** to Nairobi traffic jams :contentReference[oaicite:4]{index=4}  
- **Kes 50 million/day (~$350k)** wasted in fuel/opportunity cost :contentReference[oaicite:5]{index=5}  
- Commuters spend ~57 minutes daily in traffic, driving ~Kes 100 billion/year productivity loss :contentReference[oaicite:6]{index=6}

---

## 8. Next Steps  

1. Incorporate local idle/fuel/emission data into simulation and metrics  
2. Add pedestrian and cyclist support with additional KPIs  
3. Sync these findings into `research-notes.md` for reference backing

---

Absolutely. Here are the **direct clickable links** used in the updated `problem-statement.md`, all Kenya-focused:

---

### 📚 **Key References (Kenya-Specific)**

1. **Kes 120 billion/year lost due to Nairobi traffic jams**
   🔗 [The Star](https://www.the-star.co.ke/news/2024-07-09-traffic-jams-cost-nairobi-sh120-billion-annually-murkomen)

2. **Daily commuter time & productivity loss (\~57 minutes avg. commute)**
   🔗 [Business Daily Africa – Data Hub](https://www.businessdailyafrica.com/bd/data-hub/nairobi-county-road-map-unlocking-traffic-city-centre-3616792)

3. **Smart traffic system coverage & analysis**
   🔗 [Business Daily Africa – Opinion](https://www.businessdailyafrica.com/bd/economy/will-smart-traffic-control-system-end-nairobi-s-gridlock--2175330)

4. **Fuel and opportunity costs from Nairobi traffic (\~Kes 50 million/day)**
   🔗 [Nairobi Wire](https://nairobiwire.com/2024/07/the-billions-of-shillings-nairobi-loses-due-to-traffic-jams.html)

5. **Infrastructure context: Expressway development, transport congestion**
   🔗 [People Daily](https://peopledaily.digital/news/kenyas-expressway-to-infrastructural-excellence-2)

---

