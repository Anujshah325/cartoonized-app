
import React, { useState, useEffect } from "react";
import axios from "axios";

function App() {
  const [image, setImage] = useState(null);
  const [cartoonImage, setCartoonImage] = useState(null);
  const [lineSize, setLineSize] = useState(7);
  const [blurValue, setBlurValue] = useState(7);
  const [k, setK] = useState(12);
  const [loading, setLoading] = useState(false);
  const [dark, setDark] = useState(false);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
  }, [dark]);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onloadend = () => {
      setImage(reader.result.split(",")[1]);
    };
    reader.readAsDataURL(file);
  };

  const handleCartoonify = async () => {
    if (!image) return;
    setLoading(true);
    try {
      const response = await axios.post("http://localhost:5000/cartoonify", {
        image: image,
        params: {
          line_size: lineSize,
          blur_value: blurValue,
          k: k,
        },
      });
      setCartoonImage(response.data.cartoon);
    } catch (error) {
      console.error("Error cartoonifying image:", error);
    }
    setLoading(false);
  };

  const handleDownload = () => {
    if (!cartoonImage) return;
    const link = document.createElement("a");
    link.href = `data:image/png;base64,${cartoonImage}`;
    link.download = "cartoonized.png";
    link.click();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-100 to-purple-100 dark:from-gray-900 dark:to-gray-800 text-gray-800 dark:text-gray-100 flex flex-col items-center py-10 px-4">
      <div className="flex justify-between w-full max-w-2xl mb-4">
        <h1 className="text-3xl font-bold">🎨 Cartoonizer App</h1>
        <button
          onClick={() => setDark(!dark)}
          className="bg-gray-300 dark:bg-gray-700 px-4 py-1 rounded"
        >
          {dark ? "☀️ Light" : "🌙 Dark"}
        </button>
      </div>

      <div className="bg-white dark:bg-gray-900 shadow-lg rounded-xl p-6 w-full max-w-xl">
        <input
          type="file"
          accept="image/*"
          onChange={handleImageChange}
          className="block w-full mb-4"
        />

        <div className="space-y-4">
          <div>
            <label className="block font-medium">🖊️ Edge Line Size: {lineSize}</label>
            <input type="range" min="1" max="15" value={lineSize} onChange={(e) => setLineSize(e.target.value)} className="w-full" />
          </div>

          <div>
            <label className="block font-medium">💧 Blur Value: {blurValue}</label>
            <input type="range" min="1" max="15" value={blurValue} onChange={(e) => setBlurValue(e.target.value)} className="w-full" />
          </div>

          <div>
            <label className="block font-medium">🎨 Number of Colors: {k}</label>
            <input type="range" min="2" max="20" value={k} onChange={(e) => setK(e.target.value)} className="w-full" />
          </div>

          <button
            onClick={handleCartoonify}
            className="w-full mt-4 bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 transition"
          >
            Cartoonize
          </button>
        </div>
      </div>

      {loading && <p className="mt-6">⏳ Processing image...</p>}

      {cartoonImage && (
        <div className="mt-8 w-full max-w-3xl text-center">
          <h3 className="text-xl font-semibold mb-4">🖼️ Cartoonized Image</h3>
          <img src={`data:image/png;base64,${cartoonImage}`} alt="Cartoonized" className="rounded-lg shadow-md mx-auto max-w-full" />
          <button
            onClick={handleDownload}
            className="mt-4 bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition"
          >
            ⬇️ Download Image
          </button>
        </div>
      )}
    </div>
  );
}

export default App;



