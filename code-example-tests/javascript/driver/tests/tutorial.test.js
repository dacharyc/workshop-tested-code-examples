import { runTutorial } from '../examples/tutorial.js';
import unorderedArrayOutputMatches from '../utils/outputMatchesExampleOutput.js';
import { loadSampleData } from '../examples/tutorial-setup.js';
import { MongoClient } from 'mongodb';

describe('Aggregation pipeline filter tutorial tests', () => {
  afterEach(async () => {
    const uri = process.env.CONNECTION_STRING;
    const client = new MongoClient(uri);
    const db = client.db('agg_tutorials_db');

    await db.dropDatabase();
    await client.close();
  });

  it('Should return output that matches the expected output', async () => {
    await loadSampleData();
    const result = await runTutorial();
    const outputFilepath = 'tutorial-output.sh';
    const arraysMatch = unorderedArrayOutputMatches(outputFilepath, result);
    expect(arraysMatch).toBeTruthy();
  });
});
