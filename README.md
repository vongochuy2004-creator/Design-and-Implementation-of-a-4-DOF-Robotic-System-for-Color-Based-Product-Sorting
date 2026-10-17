# 4-DOF Robotic System for Color-Based Product Sorting

## Overview

This project presents a 4-DOF robotic pick-and-place system designed to automatically sort products by color on a conveyor belt. The system integrates a Dobot Magician robotic arm with a linear sliding rail, a computer vision module based on YOLOv11, Arduino-based motion control, and a PyQt5 human-machine interface (HMI).

The vision module identifies products belonging to three color categories: **red, blue, and yellow**. When a product reaches the designated picking position, a proximity sensor triggers the sorting sequence. The controller coordinates robot movement and an electromagnet end-effector to pick and place the product into its corresponding sorting location.

The project demonstrates the integration of robotics, computer vision, embedded systems, kinematics, and automation control in a laboratory-scale application.

## Key Features

- **4-DOF robotic system:** A 3-DOF Dobot Magician mounted on a linear rail to extend its workspace.
- **AI-based color recognition:** YOLOv11-based detection of red, blue, and yellow products.
- **Automated pick-and-place:** Color-dependent product sorting using an electromagnet end-effector.
- **Conveyor integration:** Product transportation and presence detection using an E18-D80NK proximity sensor.
- **Embedded motion control:** Two Arduino Uno R3 boards in a master–slave architecture.
- **Desktop HMI:** A PyQt5 interface for system monitoring and manual/automatic operation.
- **Kinematic analysis:** Forward kinematics, inverse kinematics, and workspace verification.

## System Architecture

The system consists of four main subsystems.

### 1. Robotic Manipulator

The robotic mechanism uses a Dobot Magician arm with three rotational degrees of freedom and an additional linear sliding axis. The linear rail expands the robot's reachable workspace and enables access to multiple product placement positions.

### 2. Computer Vision

A camera mounted above the conveyor captures images of incoming products. A YOLOv11 model classifies the products into red, blue, and yellow categories. The detected color is then used to determine the corresponding sorting destination.

### 3. Embedded Control and Actuation

Two Arduino Uno R3 boards coordinate the system through a master–slave architecture:

- **Master controller:** Controls the robot arm and linear rail using stepper motors.
- **Slave controller:** Manages conveyor operation, sensor inputs, and communication with the master controller.

The robot axes are driven by DRV8825 stepper drivers, while the conveyor uses a TB6600 driver. An electromagnet controlled through a relay module serves as the end-effector for picking compatible metallic objects.

### 4. Human-Machine Interface

The PC-based control application is developed using Python and PyQt5. It provides a graphical interface for system operation, camera visualization, status monitoring, and manual control.

## Technology Stack

| Category | Technologies |
|---|---|
| Programming | Python, Arduino C/C++ |
| Computer Vision | YOLOv11 |
| Desktop HMI | PyQt5, Qt Designer |
| Embedded Control | Arduino Uno R3 |
| Motion Control | CNC Shield V3, DRV8825, TB6600 |
| Robotics | Dobot Magician, linear sliding rail |
| Mechanical Design | SolidWorks |
| Kinematic Verification | MATLAB, MATLAB Simulink |
| Sensors and Actuation | E18-D80NK proximity sensor, electromagnet |

## System Workflow

1. **Product transportation:** The conveyor moves products into the detection area.
2. **Object detection:** The proximity sensor detects a product at the designated picking position.
3. **Color recognition:** The camera captures an image, and the YOLOv11-based vision module identifies the product color.
4. **Motion calculation:** The control software determines the target position and calculates the required robot joint configuration using inverse kinematics.
5. **Pick operation:** The robot moves to the picking position and activates the electromagnet.
6. **Product sorting:** The robot transports the product to the destination assigned to its color and releases it.
7. **Cycle continuation:** The system proceeds to the next product.

## Kinematics and Motion Control

Forward and inverse kinematics were developed for the robotic manipulator using the Modified Denavit–Hartenberg (MDH) convention and homogeneous transformation matrices.

The kinematic model was verified in MATLAB, while workspace analysis was used to evaluate the robot's reachable region.

Stepper motor pulse calculations incorporate the configured microstepping mode and the 90:16 belt–pulley transmission ratio used by the arm joints.

## Experimental Results

The project report documents the following results:

| Evaluation Metric | Reported Result |
|---|---:|
| Red color detection accuracy | 96% |
| Blue color detection accuracy | 90% |
| Yellow color detection accuracy | 100% |
| Average pick-and-place positioning deviation | 2–3 mm |
| Target positioning tolerance | ±5 mm |
| Approximate automatic sorting throughput | 450 products/hour |

The results indicate that the prototype achieved the specified positioning tolerance during the reported tests and demonstrated automatic color-based sorting under laboratory conditions.

## Limitations

The current implementation has several limitations:

- Classification is limited to red, blue, and yellow products.
- The system is designed for lightweight objects compatible with the electromagnet end-effector.
- Product position variations on the conveyor can affect picking accuracy.
- Synchronization delays between the vision module and object detection sensor can affect cycle consistency.
- The prototype uses open-loop motor control without force or torque feedback.

The system is intended for educational and laboratory demonstrations rather than direct industrial deployment.

## Future Improvements

Potential improvements identified for further development include:

- Integrating encoder-based position feedback.
- Improving synchronization between conveyor motion and robot movement.
- Increasing robustness to variations in product position and operating conditions.
- Extending recognition to additional product characteristics.
- Improving cycle consistency and overall system reliability.

## Project Context

This was a team-based robotics course project focused on the design and integration of a vision-guided robotic sorting system.

The project combines mechanical design, robot kinematics, machine vision, embedded control, and HMI development into a single automation prototype.

## Repository Contents

The repository should contain the available source code, robot control software, vision model configuration, mechanical design files where shareable, and documentation.

Please refer to the actual repository files for the implemented code and setup instructions.
