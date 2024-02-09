import socket
import threading
import cv2
import numpy as np
import tkinter as tk
from tkinter import messagebox, simpledialog
import pyaudio

class VideoConferenceServer:
    def __init__(self, host, video_port, audio_port):
        self.host = host
        self.video_port = video_port
        self.audio_port = audio_port
        self.clients = []
        self.video_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.audio_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.video_server_socket.bind((self.host, self.video_port))
        self.audio_server_socket.bind((self.host, self.audio_port))
        self.video_server_socket.listen(5)
        self.audio_server_socket.listen(5)
        print(f"Server is working at {self.host}:{self.video_port} and {self.host}:{self.audio_port} addresses...")

    def handle_video_client(self, client_socket, client_address):
        print(f"{client_address} connected with video.")
        self.clients.append(client_socket)
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                continue 
            frame = cv2.resize(frame, (320, 240))
            encoded_frame = cv2.imencode('.jpg', frame)[1].tobytes()
            for client in self.clients:
                try:
                    client.sendall(encoded_frame)
                except Exception as e:
                    print(f"Hata: {e}")
                    self.clients.remove(client)
                    client.close()
                    break
        cap.release()
    def handle_audio_client(self, client_socket, client_address):
        print(f"{client_address} connected with audio.")
        self.clients.append(client_socket)
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        audio = pyaudio.PyAudio()
        stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        while True:
            data = stream.read(CHUNK)
            for client in self.clients:
                try:
                    client.sendall(data)
                except Exception as e:
                    print(f"Hata: {e}")
                    self.clients.remove(client)
                    client.close()
                    break
        stream.stop_stream()
        stream.close()
        audio.terminate()

    def start(self):
        video_thread = threading.Thread(target=self.video_thread)
        audio_thread = threading.Thread(target=self.audio_thread)
        video_thread.start()
        audio_thread.start()

    def video_thread(self):
        while True:
            client_socket, client_address = self.video_server_socket.accept()
            client_handler = threading.Thread(target=self.handle_video_client, args=(client_socket, client_address))
            client_handler.start()

    def audio_thread(self):
        while True:
            client_socket, client_address = self.audio_server_socket.accept()
            client_handler = threading.Thread(target=self.handle_audio_client, args=(client_socket, client_address))
            client_handler.start()

class VideoConferenceClient:
    def __init__(self, host, video_port, audio_port, username):
        self.host = host
        self.video_port = video_port
        self.audio_port = audio_port
        self.username = username

    def start(self):
        self.video_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.audio_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.video_client_socket.connect((self.host, self.video_port))
        self.audio_client_socket.connect((self.host, self.audio_port))
        print(f"Sunucuya bağlandı: {self.host}:{self.video_port} ve {self.host}:{self.audio_port}")
        recv_video_thread = threading.Thread(target=self.receive_video)
        recv_audio_thread = threading.Thread(target=self.receive_audio)
        recv_video_thread.start()
        recv_audio_thread.start()

    def receive_video(self):
        while True:
            try:
                data = b""
                while True:
                    packet = self.video_client_socket.recv(4096)
                    if not packet: break
                    data += packet
                    while True:
                        frame, data = self.extract_frame(data)
                        if frame is None: break
                        cv2.imshow("Video", frame)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
            except Exception as e:
                print(f"Hata: {e}")
                break
        self.video_client_socket.close()
        cv2.destroyAllWindows()

    def extract_frame(self, data):
        start = data.find(b'\xff\xd8')
        end = data.find(b'\xff\xd9')
        if start != -1 and end != -1:
            frame = data[start:end+2]
            data = data[end+2:]
            return cv2.imdecode(np.frombuffer(frame, dtype=np.uint8), cv2.IMREAD_COLOR), data
        return None, data

    def receive_audio(self):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        audio = pyaudio.PyAudio()
        stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
        while True:
            try:
                data = self.audio_client_socket.recv(CHUNK)
                stream.write(data)
            except Exception as e:
                print(f"Hata: {e}")
                break
        stream.stop_stream()
        stream.close()
        audio.terminate()
        self.audio_client_socket.close()

def host_meeting(video_port, audio_port):
    server = VideoConferenceServer('', video_port, audio_port)
    server.start()
    messagebox.showinfo("Connection informations", f":\nVideo Port: {video_port}\nAudio Port: {audio_port}")

def join_meeting(host, video_port, audio_port, username):
    client = VideoConferenceClient(host, video_port, audio_port, username)
    client.start()

def open_settings():
    settings_window = tk.Toplevel(root)
    settings_window.title("Setttings")
    settings_window.geometry("300x200")
    label = tk.Label(settings_window, text="Main settings")
    label.pack(pady=10)
    camera_label = tk.Label(settings_window, text="Camera selection:")
    camera_label.pack(pady=5)
    camera_var = tk.StringVar()
    camera_var.set("Kamera 1")
    camera_option1 = tk.Radiobutton(settings_window, text="Camera 1", variable=camera_var, value="Kamera 1")
    camera_option1.pack()
    camera_option2 = tk.Radiobutton(settings_window, text="Camera 2", variable=camera_var, value="Kamera 2")
    camera_option2.pack()
    microphone_label = tk.Label(settings_window, text="Microphone selection:")
    microphone_label.pack(pady=5)
    microphone_var = tk.StringVar()
    microphone_var.set("Mikrofon 1")
    microphone_option1 = tk.Radiobutton(settings_window, text="Micrphone 1", variable=microphone_var, value="Mikrofon 1")
    microphone_option1.pack()
    microphone_option2 = tk.Radiobutton(settings_window, text="Micrphone 2", variable=microphone_var, value="Mikrofon 2")
    microphone_option2.pack()
    volume_label = tk.Label(settings_window, text="Volume:")
    volume_label.pack(pady=5)
    volume_scale = tk.Scale(settings_window, from_=0, to=100, orient=tk.HORIZONTAL)
    volume_scale.set(50)  
    volume_scale.pack()
    username_label = tk.Label(settings_window, text="Username:")
    username_label.pack(pady=5)
    username_entry = tk.Entry(settings_window)
    username_entry.pack()
    save_button = tk.Button(settings_window, text="Save and quit", command=settings_window.destroy)
    save_button.pack(pady=10)
def main():
    global root
    root = tk.Tk()
    root.title("LocalMeeting")
    root.geometry("400x400")

    host_label = tk.Label(root, text="Create a LocalMeeting")
    host_label.grid(row=0, column=0, columnspan=2, pady=10, padx=10)

    video_port_label = tk.Label(root, text="Video Port:")
    video_port_label.grid(row=1, column=0, padx=10)

    video_port_entry = tk.Entry(root)
    video_port_entry.grid(row=1, column=1, padx=10)

    audio_port_label = tk.Label(root, text="Audio Port:")
    audio_port_label.grid(row=2, column=0, padx=10)

    audio_port_entry = tk.Entry(root)
    audio_port_entry.grid(row=2, column=1, padx=10)

    host_button = tk.Button(root, text="HOST MEETING", command=lambda: host_meeting(int(video_port_entry.get()), int(audio_port_entry.get())))
    host_button.grid(row=3, column=0, columnspan=2, pady=10)

    join_label = tk.Label(root, text="Join meeting")
    join_label.grid(row=4, column=0, columnspan=2, pady=10, padx=10)

    host_ip_label = tk.Label(root, text="Host IP address:")
    host_ip_label.grid(row=5, column=0, padx=10)

    host_ip_entry = tk.Entry(root)
    host_ip_entry.grid(row=5, column=1, padx=10)

    join_video_port_label = tk.Label(root, text="Video Port:")
    join_video_port_label.grid(row=6, column=0, padx=10)

    join_video_port_entry = tk.Entry(root)
    join_video_port_entry.grid(row=6, column=1, padx=10)

    join_audio_port_label = tk.Label(root, text="Audio Port:")
    join_audio_port_label.grid(row=7, column=0, padx=10)

    join_audio_port_entry = tk.Entry(root)
    join_audio_port_entry.grid(row=7, column=1, padx=10)

    username_label = tk.Label(root, text="Username:")
    username_label.grid(row=8, column=0, padx=10)

    username_entry = tk.Entry(root)
    username_entry.grid(row=8, column=1, padx=10)

    join_button = tk.Button(root, text="JOIN MEETING", command=lambda: join_meeting(host_ip_entry.get(), int(join_video_port_entry.get()), int(join_audio_port_entry.get()), username_entry.get()))
    join_button.grid(row=9, column=0, columnspan=2, pady=10)

  
    settings_button = tk.Button(root, text="Settings", command=open_settings)
    settings_button.grid(row=10, column=0, columnspan=2, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
