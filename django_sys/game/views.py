from django.shortcuts import render
from . import models
import json
from django.http import JsonResponse

class character:
    x = 0
    y = 0
    state = 'u'
    type = 1

class treasure:
    x = 0
    y = 0
    collected = 0

class point:
    x = 0
    y = 0

class map:
    id = 0
    name = 'map'
    length = 10
    width = 10
    state = 0
    start = point()
    end = point()
    character = character()
    treature = treasure()

def inspect(map):
    x = map.character.x
    y = map.character.y
    direction = map.character.state
    if direction == 'u':
        if y < map.width-1:
            result = map.state[x][y+1]
        else:
            result = 0
    if direction == 'd':
        if y > 0:
            result = map.state[x][y-1]
        else:
            result = 0
    if direction == 'l':
        if x > 0:
            result = map.state[x-1][y]
        else:
            result = 0
    if direction == 'r':
        if x < map.length-1:
            result = map.state[x+1][y]
        else:
            result = 0
    return result


def code_action(map, codeList):
    actionList = []
    x = map.character.x
    y = map.character.y
    direction = map.character.state
    while len(codeList) != 0:
        code = codeList.pop(0)
        if code.goStraight != 0:
            if code.goStraight_num != -1:
                number = code.goStraight_num
            else:
                number = 1
            i = 0
            if direction == 'u':
                while i < number:
                    if y < map.weight-1 and map.state[x][y+1] != 2:
                        y = y + 1
                        i = i + 1
                        actionList.append('goUp')
                    else:
                        break
            elif direction == 'd':
                while i < number:
                    if y > 0 and map.state[x][y-1] != 2:
                        y = y - 1
                        i = i + 1
                        actionList.append('goDown')
                    else:
                        break
            elif direction == 'l':
                while i < number:
                    if x > 0 and map.state[x-1][y] != 2:
                        x = x - 1
                        i = i + 1
                        actionList.append('goLeft')
                    else:
                        break
            elif direction == 'r':
                while i < number:
                    if x < map.length-1 and map.state[x+1][y] != 2:
                        x = x + 1
                        i = i + 1
                        actionList.append('goRight')
                    else:
                        break
            map.character.x = x
            map.character.y = y
        elif code.turnLeft == 1:
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
        elif code.turnRight == 1:
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
        elif code.inspect == 1:
            result = inspect(map)
            if result == 1:
                actionList.append('isBlank')
            elif result == 2:
                actionList.append('isObstacle')
            elif result == 3:
                actionList.append('isTreasure')
            elif result == 0:
                actionList.append('isEdge')
        elif code.condition is not None:
            inspect_result = inspect(map)
            if code.condition.expression == 1:
                if inspect_result == code.condition.val:
                    inner_code = code.condition.code
                else:
                    inner_code = code.condition.else_code
            elif code.condition.expression == 2:
                if inspect_result != code.condition.val:
                    inner_code = code.condition.code
                else:
                    inner_code = code.condition.else_code
            code_result = code_action(map, inner_code)
            map = code_result.map
            x = map.character.x
            y = map.character.y
            direction = map.character.state
            for i in code_result.actionList:
                actionList.append(i)
        elif code.circulate is not None:
            while 1:
                inspect_result = inspect(map)
                if code.circulate.expression == 1:
                    if inspect_result == code.circulate.val:
                        inner_code = code.circulate.code
                    else:
                        break
                elif code.circulate.expression == 2:
                    if inspect_result != code.circulate.val:
                        inner_code = code.circulate.code
                    else:
                        break
                code_result = code_action(map, inner_code)
                map = code_result.map
                x = map.character.x
                y = map.character.y
                direction = map.character.state
                for action in code_result.actionList:
                    actionList.append(action)
        elif code.open == 1:
            if map.state[x][y] == 3:
                actionList.append('collectSuccess')
                map.treasure.collected = 1
            else:
                actionList.append('collectFail')
    return {'map': map, 'actionList': actionList}

def transfer(map):
    result = map()
    result.id = map.id
    result.name = map.name
    result.width = map.width
    result.length = map.length
    result.state = [[map.state[i*map.length+j-1] for j in range(0,map.width)] for i in range(0,map.length)]
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

def game(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            map = models.Map.objects.get(id=data.id)
        except:
            return JsonResponse({'state': 'error', 'message': 'map not exist'})
        map = transfer(map)
        result = code_action(map, data.codeList)
        x = result.map.character.x
        y = result.map.character.y
        if map.end.x == x and map.end.y == y:
            if map.treasure is not None:
                if result.map.treasure.collected == 1:
                    result.actionList.append('endMissionSuccess')
                    JsonResponse({'state': 'end', 'message': 'success', 'map': result.map, 'actionList': result.actionList})
                else:
                    result.actionList.append('endMissionFail')
                    JsonResponse({'state': 'end', 'message': 'treasure not collected', 'map': result.map, 'actionList': result.actionList})
            else:
                result.actionList.append('endMissionSuccess')
                JsonResponse({'state': 'end', 'message': 'success', 'map': result.map, 'actionList': result.actionList})
        else:
            result.actionList.append('endMissionFail')
            JsonResponse({'state': 'end', 'message': 'destination not arrive', 'map': result.map, 'actionList': result.actionList})

# Create your views here.
