# Project Overview
This project is a Flask-based web application that integrates with the Azuracast API to provide real-time data on broadcasters and upcoming broadcasts. It also manages Firebase notifications for upcoming events and broadcasts, ensuring users are notified in a timely manner.

# Project Structure
__main__.py: The main entry point for the Flask application. It handles routes for retrieving broadcaster data, upcoming broadcasts, and podcast feeds. The application is configured using a config.ini file and utilizes a Firebase manager for notifications.

azuracast_data_manager.py: This file defines the AzuracastDataManager class, which handles fetching and processing data from the Azuracast API. It runs a background thread to periodically update broadcaster and broadcast information.

firebase_notification_manager.py: Defines the FirebaseNotificationManager class, which is responsible for sending notifications to Firebase. It includes logic to prevent duplicate notifications and ensure notifications are sent only when necessary.

utils.py: Contains utility functions for extracting information from the Azuracast API, parsing RSS feeds, and working with HTML content. It also includes functions for determining the orientation of text based on the presence of Arabic or Hebrew characters.

# Key Features
### Real-Time Data Fetching: 
The application fetches broadcaster data and upcoming broadcasts from the Azuracast API.

### RSS Feed Parsing: 
The application can parse RSS feeds to extract podcast data and present it to users.

### Firebase Notifications:
When a broadcast is about to start, the application sends a push notification via Firebase to alert users.

### Multi-Language Support: 
The project includes support for detecting text direction (RTL or LTR) for Arabic and Hebrew content.

# Configuration
The application uses a config.ini file for configuration. Key sections include:
ServerSettings: Contains settings for Firebase notifications, including the delay between notifications.
RSS: Path to the file containing RSS feed URLs.

# How to Run
## Install Dependencies:
Make sure to install the required Python packages using pip install.

### Setup Firebase:
Add your Firebase service account credentials to the serviceAccountKey.json file.

### Run the Application:
Execute python __main__.py to start the Flask server.

### Access the Application:
The application will be accessible at http://0.0.0.0:5001/ internally or externally at http://[your IP]:5001/.

# Example Routes
Home (/): Returns "Hello, World!".
Broadcasters (/broadcasters): Fetches and returns a list of active broadcasters.
Upcoming Broadcasts (/upcomingBroadcasts): Returns the three upcoming broadcasts.
Podcast List (/podcastList): Provides data from the parsed RSS feeds.

# Dependencies
Flask
Flask-CORS
Firebase Admin SDK
BeautifulSoup (for HTML parsing)
Requests (for making HTTP requests)
dotenv (for environment variable management)
