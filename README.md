# CarVision
Maintaining a safe distance from the vehicle ahead
is critical for safe driving. While LiDAR sensors can be used
for distance measurement, their high cost and the large number
of vehicles without such sensors—especially in developing re-
gions—necessitate a low-cost yet effective alternative. To address
this, we introduce CarVision , a system that utilizes a commer-
cially available single-chip mmWave radar mounted on a car’s
dashboard for vehicle ranging. CarVision detects vehicles within
the radar’s field of view (FoV) and computes both the distance
and relative speed of the vehicles in front. Our system employs
a novel hybrid approach for vehicle detection and tracking,
combining deep neural network-based detection with range
tracking in a streamlined pipeline to optimize both accuracy and
speed. Additionally, we’ve developed a smartphone-based alert
system that warns drivers if a vehicle approaches within a crit-
ical distance (approximately 2 meters). CarVision demonstrates
reliable ranging performance in both daytime and nighttime
conditions, with accurate measurements up to 10 meters.

More details on experimental results and description is provided [here](./MoreDetails.md) 


## Data Collection Setup

To install mmWave Demo Visualizer from Texas Instruments, first go to this [link](https://dev.ti.com/gallery/view/mmwave/mmWave_Demo_Visualizer/) and select SDK [2.1.0](https://dev.ti.com/gallery/view/mmwave/mmWave_Demo_Visualizer/ver/2.1.0/). Now go to Help and select Download or Clone Visualizer. Finally you need to download and install the entire repository in your machine.

Now copy all the content of the provided submodule `mmWave-Demo-Visualizer` and paste it in the installaed mmWave-demo-visualizer directory i.e. **C:\Users\UserName\guicomposer\runtime\gcruntime.v11\mmWave_Demo_Visualizer**

Once you are done with the installation run 
```bash
launcher.exe
```
Finally using this tool you can save mmWave data in your local machine. Data will be saved in a txt file in JSON format.


For questions and general feedback, contact Rajib Sarkar (srajib826@gmail.com).




