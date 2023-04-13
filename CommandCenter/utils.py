import roslibpy
import rosclient

def getGoalObject(x,y,w,z):
    goal_msg = roslibpy.Message(
        {
            'target_pose':{
                'header':{
                    'frame_id':'map',
                    'seq':rosclient.client.id_counter,
                    'stamp':rosclient.client.get_time()  
                },
                'pose':{
                    'orientation':{
                        'w':w,
                        'z':z,
                        'y':0,
                        'x':0
                    },
                    'position':{
                        'x':x,
                        'y':y,
                        'z':0
                    }
                }
            }
        }
    )
    goal = roslibpy.actionlib.Goal(rosclient.action_client,goal_msg)
    return goal
