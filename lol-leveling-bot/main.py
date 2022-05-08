import robot
import utilities
import listener


if __name__ == '__main__':
    # Perform setup
    utilities.setup()

    # Create listener thread
    listener.create_thread()

    # Run bot
    robot.run()
