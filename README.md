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

<div align="center">
    <img src="assets/system_overview-1.png"  System Overview" width="600">
</div>

More details on experimental results, baseline implementation and implementation of <i>CarVision</i> is provided [here](./MOREDETAILS.md).

## License and Ethical Approval

The codebase and dataset is free to download and can be used with GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007 for non-commercial purposes. All participants involved in providing the driving data signed forms consenting to the use of collected vehicle sensor data for non-commercial research purposes. The Institute's Ethical Review Board (IRB) at IIT Kharagpur, India has approved the data collection, with the Approval Number: <b>IIT/SRIC/DEAN/2023, dated July 31, 2023</b>.

## Reference
To refer <i>CarVision</i> framework or the dataset, please cite the following work.

BibTex Reference:
```
@inproceedings{sarkar2025CarVision, 
title={CarVision : Vehicle Ranging and Tracking Using mmWave Radar for Enhanced Driver Safety}, 
author={Sarkar, Rajib and Sen, Argha and Chakraborty, Sandip},
year={2025},
} 
```

For questions and general feedback, contact Rajib Sarkar (srajib826@gmail.com).



