import os
import time
import subprocess

# Open log file in append mode
logfile = open("full_run_log.txt", "a")

for i in range(200):
    header = f"\n--- Run {i+1}/200 ---\n"
    print(header)
    logfile.write(header)
    logfile.flush()

    print("🔄 Restarting Tor service...")
    logfile.write("🔄 Restarting Tor service...\n")
    logfile.flush()
    os.system("sudo service tor restart")
    time.sleep(10)

    print("🌐 Fetching new Tor IP...")
    logfile.write("🌐 Fetching new Tor IP...\n")
    logfile.flush()
    ip = os.popen("curl --socks5 127.0.0.1:9050 https://api.ipify.org").read().strip()
    print(f"✅ New Tor IP: {ip}")
    logfile.write(f"✅ New Tor IP: {ip}\n")
    logfile.flush()

    print("🤖 Launching ultimate_bot.py via Tor...\n")
    logfile.write("🤖 Launching ultimate_bot.py via Tor...\n")
    logfile.flush()

    process = subprocess.Popen(
        ["python3", "-u" , "ultimate_bot_tor.py", "--batch", "--headless", "--browser", "--tor"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )

    for line in iter(process.stdout.readline, ''):
        print(line, end='')           # Terminal output
        logfile.write(line)           # Log file output
        logfile.flush()

    process.stdout.close()
    process.wait()

    print("⏳ Waiting 300 seconds before next run...\n")
    logfile.write("⏳ Waiting 300 seconds before next run...\n\n")
    logfile.flush()
    time.sleep(300)

logfile.close()
