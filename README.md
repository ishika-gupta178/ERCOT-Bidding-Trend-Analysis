# ERCOT-Bidding-Trend-Analysis

**ERCOT Bidding Trend Analysis: Setup and Visualization Guide**
<br>
**Step 1: Install Python 3.11**
You only need to install Python once. If Python 3.11 isn’t already installed, please follow this YouTube tutorial: https://youtu.be/m9I-YpOjXVQ?feature=shared
<br>
**Step 2: Clone or Download the Project Repository**
You only need to do this step once to get the project files on your system.
<br>
**Option A: Clone with Git (if Git is installed)**
1. Open a terminal or command prompt.
2. Run:
<br>
git clone https://github.com/ishika-gupta178/ERCOT-Bidding-Trend-Analysis.git
<br>
Running this command will automatically download the project folder and files on your system.
Please make a note of where it is downloaded.
<br>
**Option B: Download as ZIP (if Git isn’t installed)**
1. Go to the repository: https://github.com/ishika-gupta178/ERCOT-Bidding-Trend-Analysis.git
2. Click on Code -> Download ZIP
3. Unzip the downloaded folder to access the project files
<br> 
**Step 3: Install Required Python Libraries**
This step installs necessary python libraries to run the visualizations on your system. You only need 
to do this once.
<br>
1. Open a terminal or command prompt.
2. Navigate to the project folder:
 cd path/to/ERCOT-Bidding-Trend-Analysis
3. Run:
<br>
pip install -r requirements.txt
<br>
**Step 4: View Visualizations**
You can view one visualization at a time. Choose from three options:
<br>
historical_bidding_trends_viz.py: Displays bidding curves for each unit.
<br>
two_months_back_comparison.py: Compares bids on a specific date to those placed two months prior.
<br>
one_year_back_comparison.py: Compares bids on a specific date to those from one year prior.
<br>
To View a Visualization:
1. Open a terminal or command prompt.
2. Navigate to the project folder:
 cd path/to/ERCOT-Bidding-Trend-Analysis
3. Run one of the following commands, depending on which visualization you’d like to see:
 python historical_bidding_trends_viz.py
<br>
or
python two_months_back_comparison.py
<br>
or
python one_year_back_comparison.py
<br>
5. After running the command, an HTTPS link will appear on the terminal. Copy the link and paste it into any web browser to view the visualization.
<br>
To Close the Visualization:
<br>
Simply close the browser tab, then close the terminal or command prompt.
<br>
**Repeat only Step 4 whenever you’d like to view a different visualization.**
