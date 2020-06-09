from django.shortcuts import render
from . import models
import json
from django.http import JsonResponse

class CHARACTER:
    x = 0
    y = 0
    state = 'u'
    type = 1

class TREASURE:
    x = 0
    y = 0
    collected = 0

class POINT:
    x = 0
    y = 0

class MAP:
    id = 0
    name = 'map'
    length = 10
    width = 10
    state = []
    start = POINT()
    end = POINT()
    character = CHARACTER()
    treasure = TREASURE()

def inspect(map):
    x = map.character.x
    y = map.character.y
    direction = map.character.state
    if direction == 'u':
        if y < map.width-1:
            result = int(map.state[x][y+1])
        else:
            result = 0
    if direction == 'd':
        if y > 0:
            result = int(map.state[x][y-1])
        else:
            result = 0
    if direction == 'l':
        if x > 0:
            result = int(map.state[x-1][y])
        else:
            result = 0
    if direction == 'r':
        if x < map.length-1:
            result = int(map.state[x+1][y])
        else:
            result = 0
    return result


def code_action(map, codeList0):
    actionList = []
    codeList = codeList0[:] #copy list
    x = map.character.x
    y = map.character.y
    direction = map.character.state
    while len(codeList) != 0:
        code = codeList.pop(0) #code是dict类型
        if code['goStraight'] != 0:
            if code['goStraight'] != -1:
                number = int(code['goStraight'])
            else:
                number = 1
            i = 0
            if direction == 'u':
                while i < number:
                    if y < map.width-1 and map.state[x][y+1] != '2' and map.state[x-1][y] != 2:
                        y = y + 1
                        i = i + 1
                        actionList.append('goUp')
                    else:
                        break
            elif direction == 'd':
                while i < number:
                    if y > 0 and map.state[x][y-1] != '2' and map.state[x][y-1] != 2:
                        y = y - 1
                        i = i + 1
                        actionList.append('goDown')
                    else:
                        break
            elif direction == 'l':
                while i < number:
                    if x > 0 and map.state[x-1][y] != '2' and map.state[x-1][y] != 2:
                        x = x - 1
                        i = i + 1
                        actionList.append('goLeft')
                    else:
                        break
            elif direction == 'r':
                while i < number:
                    if x < map.length-1 and map.state[x+1][y] != '2' and map.state[x+1][y] != 2:
                        x = x + 1
                        i = i + 1
                        actionList.append('goRight')
                    else:
                        break
            map.character.x = x
            map.character.y = y
        elif code['turnLeft'] == 1:
            if direction == 'u':
                direction = 'l'
            elif direction == 'd':
                direction = 'r'
            elif direction == 'l':
                direction = 'd'
            elif direction == 'r':
                direction = 'u'
            actionList.append('turnLeft')
            map.character.state = direction
        elif code['turnRight'] == 1:
            if direction == 'u':
                direction = 'r'
            elif direction == 'd':
                direction = 'l'
            elif direction == 'l':
                direction = 'u'
            elif direction == 'r':
                direction = 'd'
            actionList.append('turnRight')
            map.character.state = direction
        elif code['inspect'] == 1:
            result = inspect(map)
            if result == 1:
                actionList.append('isBlank')
            elif result == 2:
                actionList.append('isObstacle')
            elif result == 3:
                actionList.append('isTreasure')
            elif result == 0:
                actionList.append('isEdge')
        elif code['condition']:
            inspect_result = inspect(map)
            if code['condition']['expression'] == 1:
                if inspect_result == code['condition']['val']:
                    inner_code = code['condition']['code']
                else:
                    inner_code = code['condition']['else_code']
            elif code['condition']['expression'] == 2:
                if inspect_result != code['condition']['val']:
                    inner_code = code['condition']['code']
                else:
                    inner_code = code['condition']['else_code']
            code_result = code_action(map, inner_code)
            map = code_result['map']
            x = map.character.x
            y = map.character.y
            direction = map.character.state
            for i in code_result['actionList']:
                actionList.append(i)
        elif code['circulate']:
            i = 0 #for safe
            while i < 999999 :
                i = i + 1
                inspect_result = inspect(map)
                if code['circulate']['expression'] == 1:
                    if inspect_result == code['circulate']['val']:
                        inner_code = code['circulate']['code']
                    else:
                        break
                elif code['circulate']['expression'] == 2:
                    if inspect_result != code['circulate']['val']:
                        inner_code = code['circulate']['code']
                    else:
                        break
                code_result = code_action(map, inner_code)
                map = code_result['map']
                x = map.character.x
                y = map.character.y
                direction = map.character.state
                for action in code_result['actionList']:
                    actionList.append(action)
        elif code['open'] == 1:
            if map.state[x][y] == 3 or map.state[x][y] == '3':
                actionList.append('collectSuccess')
                map.treasure.collected = 1
            else:
                actionList.append('collectFail')
    print("actionList:",actionList)
    return {'map': map, 'actionList': actionList}

def transfer(map):
    result = MAP()
    result.id = map.id
    result.name = map.name
    result.width = map.width
    result.length = map.length
    result.state = [[map.state[i*map.length+j] for j in range(0,map.length)] for i in range(0,map.width)]
    result.start.x = map.startx
    result.start.y = map.starty
    result.end.x = map.endx
    result.end.y = map.endy
    result.treasure.x = map.treasurex
    result.treasure.y = map.treasurey
    result.treasure.collected = 0
    result.character.type = map.characterType
    result.character.x = map.startx
    result.character.y = map.starty
    result.character.state = map.characterState
    return result

def ClassToDict(obj):
    pr = {}
    for name in dir(obj):
        value = getattr(obj, name)
        if not name.startswith('__') and not callable(value):
            if type(value).__name__ == "CHARACTER" or type(value).__name__ == "POINT" or type(value).__name__ == "TREASURE":
                value = ClassToDict(value)
            pr[name] = value
    return pr

def game(request):
    if request.method == 'POST':
        print("request:",request.body.decode("utf-8")) #for test
        data = json.loads(request.body)
        try:
            map0 = models.Map.objects.get(id=data['id'])
        except:
            return JsonResponse({'state': 'error', 'message': 'map not exist'})
        map = transfer(map0)
        result = code_action(map, data['codeList'])#dict类型
        x = result['map'].character.x 
        y = result['map'].character.y
        if map.end.x == x and map.end.y == y:
            if map.treasure is not None:
                if result['map'].treasure.collected == 1:
                    result['actionList'].append('endMissionSuccess')
                    return JsonResponse({'state': 'end', 'message': 'success', 'map': ClassToDict(result['map']), 'actionList': result['actionList']})
                else:
                    result['actionList'].append('endMissionFail')
                    return JsonResponse({'state': 'end', 'message': 'treasure not collected', 'map': ClassToDict(result['map']), 'actionList': result['actionList']})
            else:
                result['actionList'].append('endMissionSuccess')
                return JsonResponse({'state': 'end', 'message': 'success', 'map': ClassToDict(result['map']), 'actionList': result['actionList']})
        else:
            result['actionList'].append('endMissionFail')
            return JsonResponse({'state': 'end', 'message': 'destination not arrive', 'map': ClassToDict(result['map']), 'actionList': result['actionList']})
    else:
        return render(request, 'test.html',locals())#for test


def map_editer(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.user_id
        map = models.Map()
        map.id = id
        map.name = data.map.name
        map.length = data.map.length
        map.width = data.map.width
        for i in range(data.map.width):
            for j in range(data.map.length):
                map.state[i*length+j] = data.map.state[i][j]
        map.startx = data.map.start.x
        map.starty = data.map.start.y
        map.endx = data.map.end.x
        map.endy = data.map.end.y
        map.treasurex = data.map.treasure.x
        map.treasurey = data.map.treasure.y
        map.characterState = data.map.character.state
        map.characterType = data.map.character.type
        map.save()
        return JsonResponse({'message': 'success'})

# Create your views here.

# return map information
def map_info(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            map0 = models.Map.objects.get(id=data['id'])
        except:
            return JsonResponse({'message': 'map not exist'})
        map = transfer(map0)
        return JsonResponse({'message': 'map open success', 'map' : ClassToDict(map)})