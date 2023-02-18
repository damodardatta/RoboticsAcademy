import * as React from "react";
import Toolbar from "@mui/material/Toolbar";
import { Box, TextField } from "@mui/material";
import RoboticsTheme from "../../RoboticsTheme";
import PropTypes from "prop-types";
import SaveButton from "../../buttons/SaveButton";
import LoadFileButton from "../../buttons/LoadFileButton";
import PlayStopButton from "../../buttons/PlayStopButton";
import GazeboButton from "../../buttons/GazeboButton";
import ConsoleButton from "../../buttons/ConsoleButton";
import TeleOpButton from "../../buttons/TeleOpButton";
import RAMLoadIntoRobot from "../../buttons/RAM/RAMLoadIntoRobot.js";
import RAMPlay from "../../buttons/RAM/RAMPlay";
import RAMPause from "../../buttons/RAM/RAMPause";
import RAMReset from "../../buttons/RAM/RAMReset";

function RAMExerciseControl(props) {
  const { guiFreq, brainFreq, keyHandleFrequency } = React.useContext(
    props.context
  );
  return (
    <RoboticsTheme>
      <Toolbar
        sx={{
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "space-between",
          alignItems: "center",
          m: 1,
          border: "2px solid #d3d3d3",
        }}
      >
        <Box id={"editor-control"}>
          <LoadFileButton context={props.context} />
          <SaveButton context={props.context} />
        </Box>
        <Box id={"robot-control"}>
          <RAMLoadIntoRobot context={props.context} />
          <RAMPlay></RAMPlay>
          <RAMPause></RAMPause>
          <RAMReset></RAMReset>
        </Box>
        <Box id={"freq-control"}>
          <TextField
            id={"code_freq"}
            label="Brain Freq (Hz)"
            type="number"
            value={brainFreq}
            size={"small"}
            title={
              "The brain frequency is the value that tells the robot with what frequency should the code be updated"
            }
            sx={{ width: 160, m: 1 }}
            onKeyDown={keyHandleFrequency}
            color={"secondary"}
          />
          <TextField
            id={"gui_freq"}
            label="GUI Freq (Hz)"
            value={guiFreq}
            type="number"
            sx={{ width: 160, m: 1 }}
            title={
              "This value corresponds to the frequency the UI and visuals will be updated."
            }
            onKeyDown={keyHandleFrequency}
            size={"small"}
            color={"secondary"}
          />
        </Box>
        <Box id={"Sim-console-control"}>
          <GazeboButton context={props.context} />
          <ConsoleButton context={props.context} />
          {props.teleOpMode && <TeleOpButton context={props.context} />}
        </Box>
      </Toolbar>
      <PlayStopButton context={props.context} />
    </RoboticsTheme>
  );
}
RAMExerciseControl.propTypes = {
  context: PropTypes.any.isRequired,
  teleOpMode: PropTypes.bool,
};

RAMExerciseControl.defaultProps = {
  teleOpMode: false,
};

export default RAMExerciseControl;