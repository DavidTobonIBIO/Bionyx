// Import Tesseract.js
const Tesseract = require('tesseract.js');

// Path to the local image file (ensure the image is in your workspace)
const imagePath = './ji.jpeg';

// Start text recognition using Tesseract.js
Tesseract.recognize(
  imagePath,
  'spa', // Specify language
  {
    logger: m => console.log(m) // Log progress events (optional)
  }
)
.then(({ data: { text } }) => {
  // Output the detected text
  console.log('Detected Text:');
  console.log(text);
})
.catch(error => {
  // Handle errors
  console.error('Error during OCR:', error);
});
