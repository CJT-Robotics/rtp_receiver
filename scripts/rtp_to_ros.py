#!/usr/bin/env python3
import rospy
import gi
import numpy as np
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

gi.require_version('Gst', '1.0')
from gi.repository import Gst

class RTPReceiverNode:
    def __init__(self):
        rospy.init_node('rtp_receiver', anonymous=True)

        self.port = rospy.get_param('~port', 5000)
        self.camera_id = rospy.get_param('~camera_id', 'camera_0')
        
        topic_name = f"/camera/image_raw/{self.camera_id}"
        
        self.image_pub = rospy.Publisher(topic_name, Image, queue_size=1)
        self.bridge = CvBridge()
        
        Gst.init(None)

        pipeline_str = (
            f"udpsrc port={self.port} ! "
            "application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, payload=(int)96 ! "
            "rtpjitterbuffer latency=10 ! "
            "rtph264depay ! h264parse ! avdec_h264 ! "
            "videoconvert ! video/x-raw, format=BGR ! "
            "appsink name=sink emit-signals=true sync=false drop=true max-buffers=1"
        )

        rospy.loginfo(f"[{self.camera_id}] Port {self.port}...")
        rospy.loginfo(f"[{self.camera_id}] Topic: {topic_name}")

        self.pipeline = Gst.parse_launch(pipeline_str)
        
        self.sink = self.pipeline.get_by_name("sink")
        self.sink.connect("new-sample", self.on_new_sample)
        
        self.pipeline.set_state(Gst.State.PLAYING)

    def on_new_sample(self, sink):
        sample = sink.emit("pull-sample")
        buf = sample.get_buffer()
        caps = sample.get_caps()
        
        structure = caps.get_structure(0)
        width = structure.get_value("width")
        height = structure.get_value("height")
        
        success, map_info = buf.map(Gst.MapFlags.READ)
        if not success:
            return Gst.FlowReturn.ERROR
            
        try:
            frame = np.ndarray(shape=(height, width, 3), dtype=np.uint8, buffer=map_info.data)
            
            ros_image = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
            ros_image.header.stamp = rospy.Time.now()
            ros_image.header.frame_id = f"{self.camera_id}_link"
            self.image_pub.publish(ros_image)
            
        except Exception as e:
            rospy.logerr(f"[{self.camera_id}] Fehler: {e}")
        finally:
            buf.unmap(map_info)
            
        return Gst.FlowReturn.OK

    def shutdown(self):
        self.pipeline.set_state(Gst.State.NULL)

if __name__ == '__main__':
    try:
        node = RTPReceiverNode()
        rospy.spin()
        node.shutdown()
    except rospy.ROSInterruptException:
        pass
