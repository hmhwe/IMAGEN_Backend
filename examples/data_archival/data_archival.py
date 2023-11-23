import subprocess
import sys
import os


ada_url = 'https://dcacheview.grid.surfsara.nl:22880/api/v1'


# To check status of dCache, stage/unstage files and directories using ADA and Macaroon token
def AdaCommand(token_file, ada_url, ada_command = '--whoami', directory_path = '/'):
    command = ['ada','--tokenfile', token_file, '--api', ada_url, ada_command, directory_path]
    print("Command = ", command)
    try:
        # Run the ada command and capture the output
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)


        output_lines = result.stdout.split('\n')
        items = [line.strip() for line in output_lines if line.strip()]
        return items
    except subprocess.CalledProcessError as e:
        print(f"Error executing ada command: {e}")
        return None



if __name__ == "__main__":
    if len(sys.argv) !=3:
        print("Error")
        sys.exit(1)

    macaroon_token_file = sys.argv[1]
    ada_command = sys.argv[2]


    contents = AdaCommand(macaroon_token_file, ada_url, ada_command, directory_path)
    print(contents)
    if contents:
        for item in contents:
                print(item)
