import json
from channels.generic.websocket import AsyncWebsocketConsumer

# connection manager
connections = set()

def broadcast(message, sender=None):
    for connection in connections.copy():
        if connection != sender:
            try:
                connection.send(text_data=json.dumps({
                    'message': message,
                    'sender': 'system'
                }))
            except:
                connections.discard(connection)

class ProcessConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("process_group", self.channel_name)

        # add to connection pool
        connections.add(self)
        print(f'Client connected. Total connections: {len(connections)}')

        # onopen message with connection count
        await self.send(text_data=json.dumps({
            'message': f'ProcessConsumer - {len(connections)} clients connected.',
            'sender': 'system'
        }))

        # notify other clients
        for connection in connections:
            if connection != self:
                try:
                    await connection.send(text_data=json.dumps({
                        'message': f'New client. {len(connections)} total clients.',
                        'sender': 'system'
                    }))
                except:
                    connections.discard(connection)

    async def disconnect(self, code):
        connections.discard(self)
        print(f'Client disconnected. Remaining connections: {len(connections)}')

        # notify remaining clients
        for connection in connections:
            try:
                await connection.send(text_data=json.dumps({
                    'message': f'Client left. {len(connections)} total clients.',
                    'sender': 'system'
                }))
            except:
                connections.discard(connection)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            if not text_data:
                raise ValueError('No message provided')
            text_data_json = json.loads(text_data)
            message = text_data_json['message']

            print(f'Broadcasting message: {message}')

            # broadcast message to all other clients
            for connection in connections:
                if connection != self:
                    try:
                        await connection.send(text_data=json.dumps({
                            'message': f'Client says: {message}',
                            'sender': 'other'
                        }))
                    except:
                        connections.discard(connection)

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'message': 'Invalid message format',
                'sender': 'system'
            }))

    # work with the process messages during inference
    async def process_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({
            "message": message,
        }))

    async def process_progress(self, event):
        title_name = event["title_name"]
        percentages = "|".join(str(p) for p in event["percentages"])
        await self.send(text_data=json.dumps({
            "message": f'Inference progress | volumes progress object updated',
            "title_name": title_name,
            "percentages": percentages
        }))

    async def process_success(self, event):
        job_name = event["job_name"]
        job_id = event["job_id"]
        print(f'Inference completed successfully: {job_id}')
        await self.send(text_data=json.dumps({
            "message": f'Inference completed successfully: {job_name}',
            "job_id": job_id,
            "job_name": job_name,
            "success": True
        }))

    async def process_error(self, event):
        job_name = event["job_name"]
        await self.send(text_data=json.dumps({
            "message": f'Error occurred during inference: {job_name}',
            "error": True
        }))
