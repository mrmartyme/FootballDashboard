import subprocess

# Step 1: Run ScrapeNCAA.py
print("Running ScrapeNCAA.py...")
subprocess.run(["python", "ScrapeNCAA.py"], check=True)
print("Finished running ScrapeNCAA.py")

# Step 2: Run CombineIndividualTeamFiles.py
print("Running CombineIndividualTeamFiles.py...")
subprocess.run(["python", "CombineIndividualTeamFiles.py"], check=True)
print("Finished running CombineIndividualTeamFiles.py")

# Step 3: Run CombineAllTeamsData.py
print("Running CombineAllTeamsData.py...")
subprocess.run(["python", "CombineAllTeamsData.py"], check=True)
print("Finished running CombineAllTeamsData.py")
