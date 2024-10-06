# <Cosmic Respire> by Da Cosmic Guardians
## 2024 NASA Hackathon Project


Welcome to the 2024 NASA Hackathon project repository!
This project aims to make an enjoyable game for astronauts facing profound physical and mental challenges in prolonged microgravity environments.

## Table of Contents
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)


## Features
- **Login System**: Players need to log in before starting the game.
- **Game Mode Selection**: After logging in, players can select between two game modes:
  - **Coin Mode**: Collect as many coins as possible within a limited time.
  - **Obstacle Mode**: Avoid obstacles that are placed at the top and bottom of the screen.
- **Real-Time Score Tracking**: The game tracks and displays the score in real-time.
- **Gravity and Magnetic Field Simulation**: The astronaut’s movement is influenced by real-time data from solar wind plasma and magnetic fields.
- **Breathing Pattern Simulation**: The player's movement in the obstacle avoidance game is inspired by a cosine wave, simulating human breathing patterns.
- **Saving and using of End Game Score**: After the game ends, the player's score is saved for further use of analyzing player's physical and mental health.


## Technologies Used
- **Python**: For core game logic and gameplay using Pygame.
- **Pygame**: To handle game graphics, user input, and physics.
- **Flask**: For the login system, session management, and serving the game mode selection screen.
- **MongoDB**: Used to store player information and game scores.
- **HTML/CSS**: For the web-based interface, including login and mode selection screens.
- **Solar Wind and Magnetic Field Data**: Integrated real-time data to influence the astronaut's movement during gameplay.
- **TensorFlow & Keras**: For building and training a predictive model based on time, gender, and gravity data to influence the game's difficulty and obstacles.
- **Scikit-learn**: Used for splitting the data into training and testing sets and evaluating the model's performance.
- **Mean Squared Error (MSE) & Mean Absolute Error (MAE**): Used to measure the performance of the model and improve accuracy for generating realistic game environments.


## Installation
To get started with this project, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/MANI907/2024NASA_Hackathon.git

2. Navigate to the project directory
Once the repository is cloned, navigate to the project directory:

   ```bash
   cd 2024NASA_Hackathon

3. Set up a virtual environment
To avoid conflicts with your system's Python setup, it's recommended to use a virtual environment. Set up and activate the virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate

4. Install required dependencies
Once the virtual environment is activated, install the project's dependencies:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt

5. Set up MongoDB (Optional)
This project uses MongoDB to store player data and scores. Make sure MongoDB is installed and running on your machine:

Install MongoDB from the official MongoDB website.
Ensure that MongoDB is running locally (on localhost:27017).
You can verify if MongoDB is running by executing the following command:
   ```bash
   mongo

6. Run the Flask server
With everything set up, you can now run the Flask server to start the web application:
   ```bash
   python app.py

7. Access the game
Open your browser and go to http://127.0.0.1:5000/login to access the login page.
After logging in, you can select one of the game modes (Coin Mode or Obstacle Mode) to play the game.

8. Playing the game
Coin Mode: Collect as many coins as possible before the timer runs out by breathing through the platformer.(up/down arrow keys are used instead)
Obstacle Mode: Avoid obstacles while controlling the astronaut with arrow keys.

9. Save game scores
At the end of each game, the score will be saved and displayed on the web interface.
