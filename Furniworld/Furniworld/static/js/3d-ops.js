function calculateDirection(angle)
{
    /*
              90  
               |
               |
    180 --------------- 360
               |
               |
              270

    */

    if (angle <= 135 && angle > 45)
        return 'up';
    else if (angle <= 225 && angle > 135)
        return 'left';
    else if (angle <= 315 && angle > 225)
        return 'down';
    else
        return 'right';

}

function toggleMove()
{
    if (moveMode)
        moveButton.classList.remove('toggle-active');
    else
    {
        moveButton.classList.add('toggle-active');
        rotateButton.classList.remove('toggle-active');
        rotateMode = true;
    }

    moveMode = !moveMode;
}

function toggleRotate()
{
    if (rotateMode)
        rotateButton.classList.remove('toggle-active');
    else
    {
        rotateButton.classList.add('toggle-active');
        moveButton.classList.remove('toggle-active');
        moveMode = true;
    }

    rotateMode = !rotateMode;
}