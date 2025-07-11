// back.js
require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { CohereClientV2 } = require('cohere-ai');

const app = express();
app.use(cors());
app.use(express.json());

const cohere = new CohereClientV2({
    token: process.env.COHERE_API_KEY || '',
});

app.post('/api/generate-itinerary', async (req, res) => {
    const { destination, days, budget, companions } = req.body;

    if (!destination || !days || !budget || !companions) {
        return res.status(400).json({ error: 'Missing required fields' });
    }

    const prompt = `Plan a detailed ${days}-day trip to ${destination} for ${companions} on a ${budget} budget. Include daily activities, meals, and sightseeing suggestions.`;

    try {
        const response = await cohere.chat({
            model: 'command-a-03-2025',
            messages: [{ role: 'user', content: prompt }],
        });

        console.log('Cohere API response:', JSON.stringify(response, null, 2));

        if (response && response.message && response.message.content) {
            const content = response.message.content;
            let itinerary = '';

            if (Array.isArray(content)) {
                itinerary = content.map(c => c.text).join('\n');
            } else {
                itinerary = content;
            }

            res.json({ itinerary });
        } else {
            console.error('Unexpected Cohere response structure:', response);
            res.status(500).json({ error: 'Unexpected API response structure' });
        }
    } catch (error) {
        console.error('Cohere API error:', error);
        res.status(500).json({ error: 'Failed to generate itinerary' });
    }
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log(`Backend running on port ${PORT}`);
});
