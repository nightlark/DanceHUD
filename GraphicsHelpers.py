import sdl2
import sdl2.sdlttf
import sdl2.sdlimage

def initSDL2():
    # Initialize SDL2
    sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)

    # Initialize TTF rendering
    tfi = sdl2.sdlttf.TTF_Init()
    if tfi != 0:
        print "TTF_Init failed"
        exit(1)

    # Initialize SDL image
    imgi = sdl2.sdlimage.IMG_Init(sdl2.sdlimage.IMG_INIT_JPG + sdl2.sdlimage.IMG_INIT_PNG)
    if imgi != sdl2.sdlimage.IMG_INIT_JPG + sdl2.sdlimage.IMG_INIT_PNG:
        print "IMG_Init failed"

def quitSDL2():
    sdl2.sdlttf.TTF_Quit()
    sdl2.sdlimage.IMG_Quit()
    sdl2.SDL_Quit()

def renderText(message, font, color, renderer):
    # Render to a surface
    surf = sdl2.sdlttf.TTF_RenderUTF8_Blended(font, message.encode('utf8'), color)

    if surf is None:
        sdl2.sdlttf.TTF_CloseFont(font)
        print "TTF_RenderText failed"
        return None

    # Create a texture from the surface with the text
    texture = sdl2.SDL_CreateTextureFromSurface(renderer, surf)
    if texture is None:
        print "SDL_CreateTextureFromSurface failed"

    # Clean up the surface
    sdl2.SDL_FreeSurface(surf)
    return texture

def loadImageFile(imageFile, renderer):
    # Load into a surface
    surf = sdl2.sdlimage.IMG_Load(imageFile)

    if surf is None:
        print "IMG_Load failed"
        return None

    # Create a texture from the surface with the image
    texture = sdl2.SDL_CreateTextureFromSurface(renderer, surf)
    if texture is None:
        print "SDL_CreateTextureFromSurface failed"

    # Clean up the surface
    sdl2.SDL_FreeSurface(surf)
    return texture

def loadFontFile(fontFile, fontSize):
    # Open the font file
    sdl2.SDL_ClearError()
    font = sdl2.sdlttf.TTF_OpenFont(fontFile, int(fontSize))
    err = sdl2.SDL_GetError()

    if font is None or not err == '':
        print "TTF_OpenFont error: " + err
        return None

    return font


def renderTextFromFile(message, fontFile, color, fontSize, renderer):
    # Load the font file
    font = loadFontFile(fontFile, fontSize)

    if font is None:
        return None

    # Render the text
    texture = renderText(message, font, color, renderer)

    # Clean up the texture
    sdl2.sdlttf.TTF_CloseFont(font)
    return texture