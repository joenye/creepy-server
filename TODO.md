### Backlog
- Consider migrate to DynamoDB:
    - TTL (https://aws.amazon.com/blogs/aws/new-manage-dynamodb-items-using-time-to-live-ttl/)
    - Provisioned capacity
    - One entity per tile
    - Hash key per game
- Peek functionality (when way is blocked from other side)
- Fix player marker display when going up and down floors
- Actions should have interface for whether they should increase tick
- Display player avatars on UI
  - Later allow viewing party

- Implement ticket pattern for authorisation (https://devcenter.heroku.com/articles/websocket-security#authentication-authorization)

### Data model

- `*` prefix denotes new field
- `^` prefix denotes field to drop

```json
{
  "session": {
    "*current_tick": 0,
    "*current_turn": "f260c9f9",
    "*players": {
      "f260c9f9": {
        "display_name": "Joe",
        "avatar_url": "https://foo.com/cat.png",
        "current_position": "x=0,y=0,z=0",
        "party": {
          "0": {
            "type": "woman_hero",
            "items_carried": [
              "magic_shield",
              "bone_charm",
              "gold_25kg",
            ],
          },
        },
        "context": {
          "mode": "game|dialog",
          "dialogType": "approach|attack|retaliate",
        },
      },
    },
    "*history": [
      {
        "tick": 0,
        "time": "2011-10-05T14:48:00.000Z",
        "action": "navigate",
      },
    ],
    "^current_position": "x=0,y=0,z=0",
    "floors": {
      "*z=0": {
        "tiles": {
          "x=0,y=0": {
            "is_visited": true,
            "sides": {
              "up":{
                "is_blocked":true,
                "edge_position":1,
              },
              "right":{
                "is_blocked":false,
                "edge_position":2,
              },
              "down":{
                "is_blocked":false,
                "edge_position":2,
              },
              "left":{
                "is_blocked":true,
                "edge_position":2,
              },
            },
            "entity_candidates":[
              "x=200,y=100",
              "x=300,y=100",
              "x=300,y=200",
              "x=400,y=200",
              "x=500,y=200",
            ],
            "exits_pos":{
               "up":"x=100,y=400",
               "right":"x=600,y=200",
               "down":"x=200,y=0",
               "left":"x=0,y=200",
            },
            "background":"<?xml...",
            "entities": {
              "stairs_down":{
                "pos":"x=380,y=150",
              }
            },
          },
        },
      },
    },
  },
}

