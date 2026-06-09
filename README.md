# RTP Video Receiver & ROS Publisher Node

## Overview

The **RTP Receiver** is a ROS1 Noetic package designed to receive a ffmpeg stream and publish it to the ROS1 Noetic environment.

It receives an H.264 encoded RTP/UDP video stream using a GStreamer pipeline and converts the incoming frames into standard ROS `sensor_msgs/Image` messages. The package supports streaming from multiple cameras simultaneously.

**Works perfectly with our [rtp sender package](TODO)**

## Requirements

Install the required ROS packages on your operator station:

```bash
sudo apt install ros-noetic-cv-bridge ros-noetic-image-transport ros-noetic-rqt-image-view
```

Make sure the GStreamer 1.0 libraries and Python bindings are installed:

```bash
sudo apt install python3-gst-1.0 gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly
```

## Installation

Clone the repository into your Catkin workspace:

```bash
cd ~/catkin_ws/src
git clone git@github.com:CJT-Robotics/rtp_receiver.git
```

Build the workspace:

```bash
cd ~/catkin_ws
catkin_make
```

Source your workspace:

```bash
source devel/setup.bash
```

## Usage

Run FFmpeg to capture your camera device (e.g. `/dev/video0`), compress it using H.264 with zero-latency tuning, and send it.

Launch the receiver:

```bash
roslaunch rtp_receiver test.launch
```

## Configuration

### Multi-Camera Setup

The package is designed to scale. You can configure multiple cameras by editing the `test.launch` file and assigning unique UDP ports and `camera_id` parameters.

### Parameters

| Parameter   | Default    | Description                                           |
| ----------- | ---------- | ----------------------------------------------------- |
| `port`      | `5000`     | UDP port matching the incoming RTP stream from FFmpeg |
| `camera_id` | `camera_0` | Suffix for the published topic       |

## Published Topics

### `/camera/image_raw/<camera_id>`

**Type:** `sensor_msgs/Image`

## Troubleshooting
