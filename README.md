

# Video Conference Application

This is a simple video conference application implemented in Python. It allows users to create or join video conferences over a network.

## Installation

1. Clone the repository to your local machine:

```
git clone https://github.com/pyroalww/localmeeting
```

2. Install the required dependencies. You can do this using pip:

```
pip install -r requirements.txt
```

3. Run the main.py file to start the application:

```
python main.py
```

## Usage

### Creating a Conference

1. Launch the application and click on the "Create Conference" button.
2. Enter the desired video and audio port numbers when prompted.
3. Share the generated server IP address with other participants.

### Joining a Conference

1. Launch the application and click on the "Join Conference" button.
2. Enter the host's IP address along with the video and audio port numbers.
3. Click the "Join" button to connect to the conference.

### Controls

- Video: The application will automatically start streaming video from your webcam when connected to a conference.
- Audio: The application will automatically start streaming audio from your microphone when connected to a conference.
- Chat: A chat feature is available for participants to communicate during the conference.

## Troubleshooting

- If you encounter any issues with the application, please ensure that the required ports are open on your network and that your firewall settings allow incoming and outgoing connections.
- Make sure you have a stable internet connection for the best experience.

## Contributing

Contributions are welcome! If you find any bugs or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
