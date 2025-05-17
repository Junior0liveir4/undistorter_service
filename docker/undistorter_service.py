from is_wire.core import Channel, Subscription, Message, Tracer, AsyncTransport
from opencensus.ext.zipkin.trace_exporter import ZipkinExporter
from is_msgs.image_pb2 import Image
import numpy as np
import os
import cv2

def to_np(input_image):
    if isinstance(input_image, np.ndarray):
        return input_image
    if isinstance(input_image, Image):
        buffer = np.frombuffer(input_image.data, dtype=np.uint8)
        return cv2.imdecode(buffer, flags=cv2.IMREAD_COLOR)
    return np.array([], dtype=np.uint8)

def to_image(input_image, encode_format='.jpeg', compression_level=0.8):
    if isinstance(input_image, np.ndarray):
        params = [
            cv2.IMWRITE_JPEG_QUALITY, int(compression_level * 100)
        ] if encode_format == '.jpeg' else [
            cv2.IMWRITE_PNG_COMPRESSION, int(compression_level * 9)
        ]
        cimage = cv2.imencode(ext=encode_format, img=input_image, params=params)
        return Image(data=cimage[1].tobytes())
    if isinstance(input_image, Image):
        return input_image
    return Image()

camera_id = os.getenv("camera_id")
broker_uri = os.getenv("broker")
zipkin_host = os.getenv("zipkin_host")
zipkin_port = os.getenv("zipkin_port")
channel = Channel(broker_uri)

subscription = Subscription(channel=channel)
subscription.subscribe(topic='CameraGateway.{}.Frame'.format(camera_id))

dados = np.load('/matrix_cams/calib_rt{}.npz'.format(camera_id))
K = dados['K']
dist = dados['dist']
nK = dados['nK']
roi = dados['roi']

exporter = ZipkinExporter(
        service_name=f"Cam{camera_id} undistorted",
        host_name=zipkin_host,
        port=zipkin_port,
        transport=AsyncTransport,
)

while True:
    try:
        msg = channel.consume()
        if isinstance(msg, Message):
            tracer = Tracer(exporter, span_context=msg.extract_tracing())
            with tracer.span(name="undistort") as span:
                img = msg.unpack(Image)
                frame = to_np(img)

                dst = cv2.undistort(frame, K, dist, None, nK)
                x,y,w,h = roi
                dst = dst[0:h, 0:w, :]

                undistorted_image = to_image(dst)
                message = Message()
                message.pack(undistorted_image)
                message.inject_tracing(span)
                channel.publish(message, topic=f'UndistortedCamera.{camera_id}.Frame')

    except Exception as e:
        print(f"[Erro] Falha ao processar imagem: {e}")