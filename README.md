# AI Traffic Light System

An intelligent traffic light control system that uses computer vision and reinforcement learning to optimize traffic flow.

## System Architecture

The system has been restructured into modular components:

### Core Modules

- **`core/main.py`** - Main application entry point (simplified)
- **`core/simulation/traffic_sim.py`** - Traffic light simulation with pygame
- **`core/perception/counter.py`** - Vehicle detection and zone counting
- **`core/utils/data_processor.py`** - Data processing coordination
- **`core/utils/mock_zone_generator.py`** - Mock traffic data generation

### Tools

- **`tools/video_processor.py`** - Standalone video processing tool
- **`tools/zone_drawer.py`** - Zone configuration tool
- **`tools/frame_extractor.py`** - Video frame extraction

## Quick Start

### 1. Setup Environment

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the System

#### Option A: Run with Mock Data (Recommended for testing)
```bash
python core/main.py
```

This will start the traffic light simulation using mock data that updates every 2 seconds.

#### Option B: Process Video First, Then Run
```bash
# Process video to generate zone counts
python tools/video_processor.py data/raw/rtvClip1.mp4 --display

# Run the main system (it will use the processed data)
python core/main.py
```

### 3. Controls

- **ESC** - Exit the application
- **Close Window** - Exit the application

## System Features

### Traffic Light Simulation
- Real-time traffic light control based on zone vehicle counts
- Visual simulation with animated cars
- Dynamic traffic light timing based on traffic density
- Yellow light transitions between phases

### Vehicle Detection
- YOLOv8-based vehicle detection
- ByteTrack multi-object tracking
- Zone-based vehicle counting
- Support for cars, motorcycles, buses, and trucks

### Data Processing
- Thread-safe data handling
- Support for both video and mock data sources
- Automatic fallback to mock data if video unavailable
- Real-time data updates

## Configuration

### Zone Configuration
Edit `configs/zones/intersection_a.json` to define detection zones:

```json
{
  "Zone A": [[x1, y1], [x2, y2], [x3, y3], [x4, y4]],
  "Zone B": [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
}
```

### Video Processing
- Supported formats: MP4, MOV, AVI
- Place videos in `data/raw/` directory
- Default video: `data/raw/rtvClip1.mp4`

## Troubleshooting

### Common Issues

1. **Import Error: No module named 'cython_bbox'**
   - This is expected when running the main application
   - Video processing requires additional setup
   - Use mock data mode for testing

2. **Video not found**
   - System automatically falls back to mock data
   - Check video path in configuration

3. **Pygame window not appearing**
   - Ensure virtual environment is activated
   - Check for display/graphics driver issues

### Performance Optimization

- Reduce video resolution for faster processing
- Adjust update intervals in configuration
- Use mock data for development/testing

## Development

### Adding New Features

1. **New Detection Zones**: Edit zone configuration files
2. **Custom Traffic Patterns**: Modify `MockZoneGenerator`
3. **Different Traffic Light Logic**: Extend `TrafficSimulation`

### Testing

```bash
# Run unit tests
python -m pytest tests/

# Run integration tests
python -m pytest tests/integration/
```

## Dependencies

- **Python 3.10+**
- **PyTorch 2.3.0**
- **OpenCV 4.11.0**
- **Pygame 2.5.2**
- **Ultralytics 8.3.122**
- **YOLOX** (included in ByteTrack)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
