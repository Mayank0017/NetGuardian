// document.addEventListener('keydown', (event) => {
//   if (event.ctrlKey && event.key === 'b') {
//     const selectedText = window.getSelection().toString().trim();
//     if (selectedText) {
//       chrome.runtime.sendMessage({ message: 'check_text', text: selectedText }, response => {
//         if (response && response.isTextValid) {
//           // Remove any existing pop-up
//           const existingPopup = document.getElementById("selectedTextPopup");
//           if (existingPopup) {
//             existingPopup.remove();
//           }

//           // Create and display the pop-up with the selected text
//           const popup = document.createElement("div");
//           popup.id = "selectedTextPopup";
//           popup.style.cssText = `
//           position: fixed;
//           top: 10px;
//           right: 10px;
//           width: 200px; /* Adjust width as needed */
//           max-height: 200px; /* Set maximum height for scrolling */
//           background: white;
//           padding: 1rem;
//           border: 1px solid #ddd;
//           border-radius: 5px;
//           box-shadow: 0 0 5px rgba(0, 0, 0, 0.2);
//           z-index: 9999;
//           overflow-y: auto; /* Enable vertical scroll */
//         `;

//           popup.innerHTML = `
//             <p>Selected Text: ${selectedText}</p>
//             <button id="closeSelectedTextPopup">Close</button>
//           `;

//           document.body.appendChild(popup);

//           document.getElementById("closeSelectedTextPopup").addEventListener("click", () => {
//             popup.remove();
//           });
//         }
//       });
//     }
//   }
// });

// /****************************************************************************************************************************** */


chrome.runtime.sendMessage({ message: "check_url", url: window.location.href }, response => {
  if (response && response.isSafe) {
    const popup = document.createElement("div");
    popup.id = "popup"; // Added ID for CSS targeting
    popup.innerHTML = `
      <link rel="stylesheet" href="chrome-extension://dphlbaidndppjkllhmbdpjnikbgclgcg/popup.css">
      <div style="position: fixed; top: 10px; left: 10px; background: lightblue; padding: 10px; border: 1px solid #ccc; border-radius: 5px; box-shadow: 0 0 5px rgba(0, 0, 0, 0.2); z-index: 9999;">
        <p><i class="fas fa-check-circle"></i> This site is safe.</p>
        <button id="continueButton">Continue</button>
      </div>
    `;
    document.body.appendChild(popup);

    document.getElementById("continueButton").addEventListener("click", () => {
      popup.remove();
    });
  } else {
    const popup = document.createElement("div");
    popup.id = "popup"; // Added ID for CSS targeting
    popup.innerHTML = `
      <link rel="stylesheet" href="chrome-extension://dphlbaidndppjkllhmbdpjnikbgclgcg/popup.css">
      <div style="position: fixed; top: 10px; left: 10px; background: lightpink; padding: 10px; border: 1px solid #ccc; border-radius: 5px; box-shadow: 0 0 5px rgba(0, 0, 0, 0.2); z-index: 9999;">
        <p><i class="fas fa-exclamation-triangle"></i> This site looks suspicious.</p>
        <button id="closeButton">Close</button>
        <button id="continueButton">Continue</button>
      </div>
    `;
    document.body.appendChild(popup);

    document.getElementById("closeButton").addEventListener("click", () => {
      history.back();
    });

    document.getElementById("continueButton").addEventListener("click", () => {
      popup.remove();
    });
  }
});




document.addEventListener('keydown', (event) => {
  if (event.ctrlKey && event.key === 'b') {
    const selectedText = window.getSelection().toString().trim();
    if (selectedText) {
      chrome.runtime.sendMessage({ message: 'check_text', text: selectedText }, response => {
        if (response) {
          // Remove any existing pop-up
          const existingPopup = document.getElementById("selectedTextPopup");
          if (existingPopup) {
            existingPopup.remove();
          }

          // Create and display the pop-up with the selected text and prediction
          const popup = document.createElement("div");
          popup.id = "selectedTextPopup";
          popup.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            width: 300px; /* Adjust width as needed */
            max-height: 200px; /* Set maximum height for scrolling */
            background: white;
            padding: 1rem;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-shadow: 0 0 5px rgba(0, 0, 0, 0.2);
            z-index: 9999;
            overflow-y: auto; /* Enable vertical scroll */
          `;

          popup.innerHTML = `
            <p>Selected Text: ${selectedText}</p>
            <p>Prediction: ${response.isTextValid ? "Real" : "Fake"}</p>
            <button id="closeSelectedTextPopup">Close</button>
          `;

          document.body.appendChild(popup);

          document.getElementById("closeSelectedTextPopup").addEventListener("click", () => {
            popup.remove();
          });
        }
      });
    }
  }
});
