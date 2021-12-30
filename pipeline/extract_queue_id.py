import json
import pandas as pd

def extract_queue_id(session, queue_url_link = "https://static.developer.riotgames.com/docs/lol/queues.json"):
    queue_information = session.get(queue_url_link).json()

    queue_df = pd.DataFrame(queue_information)[['queueId', 'description']].set_index('queueId').rename(columns={'description':'queue_name'})

    with open('datahub/raw/resources/queue_id.json', 'w') as outfile:
        json.dump(queue_df.to_dict(), outfile)

    print('queue ids extracted...')


