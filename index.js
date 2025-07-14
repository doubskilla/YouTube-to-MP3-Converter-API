const express = require('express');
const axios = require('axios');
const cheerio = require('cheerio');

const app = express();
const PORT = process.env.PORT || 3000;

app.get('/api/convert', async (req, res) => {
  try {
    const videoUrl = req.query.url;
    if (!videoUrl) {
      return res.status(400).json({ error: 'URL is required' });
    }

    // Appel à l'API publique de conversion YouTube->MP3
    const apiUrl = `https://yt-downloader.example.com/api/convert?url=${encodeURIComponent(videoUrl)}`;
    // Remarque : Cette URL est un placeholder.
    // Tu devras remplacer ce code par l'appel effectif à l'API que tu souhaites utiliser,
    // par exemple via la solution de DiegoRosa si disponible.

    // Ici, nous simulons le scraping du HTML pour trouver le lien MP3
    const response = await axios.get(apiUrl);
    const html = response.data;
    const $ = cheerio.load(html);
    // Exemple : on recherche un lien avec une classe ou un id spécifique (à adapter)
    const mp3Link = $('a.download-link').attr('href'); 

    if (!mp3Link) {
      return res.status(500).json({ error: 'Unable to fetch MP3 link' });
    }
    return res.json({ mp3DownloadUrl: mp3Link });
  } catch (error) {
    console.error(error);
    return res.status(500).json({ error: error.toString() });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
