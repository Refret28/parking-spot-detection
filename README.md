# Installation

1) **Installing required dependencies:**
```bash
    pip install -r requirements.txt
```

2) **To mark objects in images, I recommend using the "labelImg" repository, which can be cloned by running the following command:**
```bash
    git clone https://github.com/HumanSignal/labelImg.git
```
<blockquote>
    <strong>This repository provides one of the popular tools for annotating images. Instructions for installing and using the application can be found by following the link in the subdirectory.</strong>
</blockquote>

# Basic steps to make the code work

1) **Then, for the program to work, you should enter some parameters in the configuration file "config.ini". These include the following:**<br>
•&nbsp;&nbsp;&nbsp;<strong>RTSP protocol</strong><br>
•&nbsp;&nbsp;&nbsp;<strong>Neuron network model for detecting objects in the frame</strong><br>
•&nbsp;&nbsp;&nbsp;<strong>The intersection threshold over the union, which is discussed in the next paragraph</strong>

2) **So, about the intersection over the union. This algorithm is used in the code to determine the intersection of the car's boundary boxes with the parking space. By comparing the value of the obtained coefficient (coverage degree) with the threshold value specified in config.ini, we determine whether to consider the space occupied by the car or not. That is, if the value obtained as a result of the calculation is greater than the threshold value, the space will be considered occupied, otherwise - free.**