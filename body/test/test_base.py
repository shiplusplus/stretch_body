# Logging level must be set before importing any stretch_body class
import stretch_body.robot_params
# stretch_body.robot_params.RobotParams.set_logging_level("DEBUG")

import unittest
import stretch_body.base

import time


class TestBase(unittest.TestCase):

    def test_valid_startup_status(self):
        b = stretch_body.base.Base()
        self.assertTrue(b.startup())
        self.assertNotEqual(b.status['timestamp_pc'],0)

    def test_fast_base_motion_allowed(self):
        """Verifies fast base motion is allowed at the correct time.
        """
        import stretch_body.robot
        r = stretch_body.robot.Robot()
        r.robot_params['robot_sentry']['base_max_velocity'] = 1 # Enable fast base motion
        self.assertTrue(r.startup())
        if not r.is_calibrated():
            self.fail("test requires robot to be homed")

        r.stow()
        r.pull_status()
        self.assertTrue(r.base.fast_motion_allowed)

        # check lift
        r.lift.move_to(r.base.params['sentry_max_velocity']['max_lift_height_m'] + 0.05)
        r.push_command()
        time.sleep(3)
        self.assertFalse(r.base.fast_motion_allowed)
        r.lift.move_to(r.base.params['sentry_max_velocity']['max_lift_height_m'] - 0.05)
        r.push_command()
        time.sleep(3)
        self.assertTrue(r.base.fast_motion_allowed)

        # check arm
        r.arm.move_to(r.base.params['sentry_max_velocity']['max_arm_extension_m'] + 0.05)
        r.push_command()
        time.sleep(3)
        self.assertFalse(r.base.fast_motion_allowed)
        r.arm.move_to(r.base.params['sentry_max_velocity']['max_arm_extension_m'] - 0.05)
        r.push_command()
        time.sleep(3)
        self.assertTrue(r.base.fast_motion_allowed)

        # check wrist_yaw
        r.end_of_arm.move_to("wrist_yaw", r.base.params['sentry_max_velocity']['min_wrist_yaw_rad'] - 0.1)
        time.sleep(3)
        self.assertFalse(r.base.fast_motion_allowed)
        r.end_of_arm.move_to("wrist_yaw", r.base.params['sentry_max_velocity']['min_wrist_yaw_rad'] + 0.1)
        time.sleep(3)
        self.assertTrue(r.base.fast_motion_allowed)

        r.stop()

    def test_waypoint_trajectory(self):
        """Test a basic waypoint trajectory to verify it works.
        """
        b = stretch_body.base.Base()
        b.left_wheel.disable_sync_mode()
        b.right_wheel.disable_sync_mode()
        self.assertTrue(b.startup(threaded=True))

        b.trajectory.add(0, 0, 0, 0)
        b.trajectory.add(3, 0.05, 0, 0)
        b.follow_trajectory()
        b.pull_status()
        # b.pretty_print()
        time.sleep(4)

        b.stop()
