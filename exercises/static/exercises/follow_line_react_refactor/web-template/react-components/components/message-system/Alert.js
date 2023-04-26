import * as React from "react";
import MuiAlert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Collapse from '@mui/material/Collapse';

import "../../css/modals/Message.css";

window.RoboticsReactComponents = window.RoboticsReactComponents || {};
window.RoboticsReactComponents.MessageSystem = window.RoboticsReactComponents.MessageSystem || {};
window.RoboticsReactComponents.MessageSystem.Alert = (function () {
  let alert_handler = null;

  const setAlertHandler = (callback) => {
    alert_handler = callback;
  };

  const showAlert = (message, closeAction, closeText) => {
    if (alert_handler) {
      alert_handler(message, closeAction, closeText);
    }
  };

  return {
    showAlert: showAlert,
    setAlertHandler: setAlertHandler
  }
})();

const Alert = () => {
  const [message, setMessage] = React.useState("");
  const [closeData, setCloseData] = React.useState(null);

  React.useEffect(() => {
     RoboticsReactComponents.MessageSystem.Alert.setAlertHandler((message, closeAction, closeText) => {
       if(typeof message !== "string") {
         console.error(`Bad message sent ${message}`);
         return;
       }

       setMessage(message || "No message set");

       if(closeAction && closeText)
       {
         setCloseData({
           text: closeText,
           action: closeAction
         });
       }
     });
  }, []);

  const closeAlert = () => {
    setMessage(null);
    setCloseData(null);
  };

  return (
    <div id={"message-container"} className={"bottom"}>
      {message ?
        <Collapse in={message !== null}>
          <MuiAlert
            severity="error"
            action={
              <Button color="inherit" size="small" onClick={closeData ? closeData.action : closeAlert}>
                {closeData ? closeData.text : "CERRAR"}
              </Button>
            }>
            {message}
          </MuiAlert>
        </Collapse>
        : null
      }
    </div>
  );
};

export default Alert;