
// chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
//   if (request.message === "check_url") {
//     const isSafe = isUrlSafe(request.url);
//     sendResponse({ isSafe });
//   } else if (request.message === 'check_text') {
//     const isTextValid = isTextSafe(request.text);
//     sendResponse({ isTextValid });
//   }
// });


// function isUrlSafe(url) {
  
//   return false;
// }


// function isTextSafe(text) {
  
//   return true;
// }


chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.message === "check_url") {
    const isSafe = isUrlSafe(request.url);
    sendResponse({ isSafe });
  } else if (request.message === 'check_text') {
    // Send the selected text to FastAPI server
    fetch('http://localhost:8000/predict', {  // Update the URL if needed
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text: request.text }),
    })
    .then(response => response.json())
    .then(data => {
      // Send the prediction result back to content script
      sendResponse({ isTextValid: data.prediction === "Real" });
    })
    .catch(error => {
      console.error('Error fetching prediction:', error);
      sendResponse({ isTextValid: false }); // Default to false if there's an error
    });

    // Return true to indicate that the response will be sent asynchronously
    return true;
  }
});

async function isUrlSafe(url) {
  try {
    const response = await fetch('http://localhost:8000/predict-phishing-url', {  // Update the URL if needed
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url }),
    });

    const data = await response.json();
    return data.prediction === "Legitimate"; // Return true if the URL is legitimate
  } catch (error) {
    console.error('Error fetching URL prediction:', error);
    return false; // Default to false if there's an error
  }
}