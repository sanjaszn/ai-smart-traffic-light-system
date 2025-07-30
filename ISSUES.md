# AI Traffic Light System - Active Issues

## Critical Functionality
1. **Merge Lane ≠ Intersection Mismatch**  
   - *Problem*: Simulation expects 4-way intersection but video shows single-direction merge  
   - *Impact*: Lights don't cycle, vehicles spawn incorrectly  
   - *Workaround*: Use mock data generator for RL development  

2. **Articulated Bus Double-Detection**  
   - *YOLO splits buses into multiple detections*  
   - *Fix*: Post-process with spatial clustering (nearby boxes merge)  

## Visualization
3. **Font Size Too Small**  
   - `cv2.putText(fontScale=0.6)` → Change to `1.2`  

4. **Video Window Hidden in Main Pipeline**  
   - *Cause*: OpenCV/PyGame window conflict  
   - *Fix*: `cv2.moveWindow()` or threaded display  

## Simulation Lag
5. **Delayed Vehicle Spawning**  
   - *Likely*: JSON read interval too slow  
   - *Debug*: Check `sim.update()` refresh rate  

---

> **Next**: Proceed with mock data + RL env while hunting better footage.  
> **File**: `mock_zone_generator.py` (ready for implementation)


## Memory Optimization Needed
- **Test**: `test_o1_memory` fails (~24KB growth vs 5KB limit)  
- **Impact**: Not critical for initial development but needs fixing before:  
  - Long-running deployments  
  - Edge device implementation  
- **Priority**: Medium (post-algorithm validation)  
- **Suggested Fix**: Pre-allocate buffers and reuse numpy arrays  