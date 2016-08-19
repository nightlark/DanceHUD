import os
import time
import math

from sdl2 import *
from GraphicsHelpers import *
import settings
from ctypes import c_int, pointer

class PresentationDisplay:
    def __init__(self):
        self.window = None
        self.renderer = None
        self.texture = None
        self.old_texture = None
        self.displayMode = SDL_DisplayMode()
        self.height = 0
        self.width = 0
        self.bkgndColor = SDL_Color(255, 255, 255)
        self.objects = []
        self.is_crossfading = False
        self.crossfade_type = 'Cross'
        self.crossfade_start_time = time.time()
        self.crossfade_end_time = time.time()

    def setDisplay(self, displayNum, fullscreen):
        # Destroy existing renderers/windows
        if self.texture:
            SDL_DestroyTexture(self.texture)
        if self.renderer:
            SDL_DestroyRenderer(self.renderer)
        if self.window:
            SDL_DestroyWindow(self.window)

        # Tell SDL not to minimize on focus loss
        SDL_SetHint(sdl2.SDL_HINT_VIDEO_MINIMIZE_ON_FOCUS_LOSS, "0")

        # Create the fullscreen window
        SDL_GetCurrentDisplayMode(displayNum, self.displayMode)
        self.height = self.displayMode.h
        self.width = self.displayMode.w
        flags = SDL_WINDOW_SHOWN
        if fullscreen:
            flags = flags | SDL_WINDOW_FULLSCREEN_DESKTOP
        else:
            flags = flags | SDL_WINDOW_RESIZABLE
        self.window = sdl2.SDL_CreateWindow("DanceHUD Presentation Display",
                                            SDL_WINDOWPOS_UNDEFINED_DISPLAY(displayNum),
                                            SDL_WINDOWPOS_UNDEFINED_DISPLAY(displayNum),
                                            self.width,
                                            self.height,
                                            flags)

        # Create a renderer for the window
        self.renderer = SDL_CreateRenderer(self.window, -1, SDL_RENDERER_ACCELERATED + SDL_RENDERER_TARGETTEXTURE + SDL_RENDERER_PRESENTVSYNC)
        SDL_SetRenderDrawBlendMode(self.renderer, SDL_BLENDMODE_NONE)

        # Create a texture to render to
        self.texture = SDL_CreateTexture(self.renderer, SDL_PIXELFORMAT_RGBA8888, SDL_TEXTUREACCESS_TARGET, self.width, self.height)

    def resizeWindow(self, window):
        self.width = window.data1
        self.height = window.data2


    def render(self):
        SDL_SetRenderTarget(self.renderer, self.texture)

        # Set the background clear color
        SDL_SetRenderDrawColor(self.renderer,
                               self.bkgndColor.r,
                               self.bkgndColor.g,
                               self.bkgndColor.b,
                               self.bkgndColor.a)

        SDL_RenderClear(self.renderer)

        for o in self.objects:
            o.render(self.renderer)

        SDL_SetRenderTarget(self.renderer, None)

    def beginCrossfade(self):
        self.old_texture = self.texture
        self.texture = SDL_CreateTexture(self.renderer, SDL_PIXELFORMAT_RGBA8888, SDL_TEXTUREACCESS_TARGET, self.width, self.height)
        self.crossfade_start_time = time.time()
        self.crossfade_end_time = self.crossfade_start_time + settings.CROSSFADE_DURATION
        self.is_crossfading = True
        SDL_SetTextureBlendMode(self.texture, SDL_BLENDMODE_BLEND)
        SDL_SetTextureBlendMode(self.old_texture, SDL_BLENDMODE_BLEND)
        cf_completion = int(255*((self.crossfade_end_time - time.time()) / (self.crossfade_end_time - self.crossfade_start_time)))
        SDL_SetTextureAlphaMod(self.texture, 255-cf_completion)
        SDL_SetTextureAlphaMod(self.old_texture, cf_completion)

    def present(self):
        SDL_RenderClear(self.renderer)
        if not self.is_crossfading:
            SDL_RenderCopy(self.renderer, self.texture, None, None)
        else:
            SDL_RenderCopy(self.renderer, self.texture, None, None)
            SDL_RenderCopy(self.renderer, self.old_texture, None, None)
            cf_completion = int(255*((self.crossfade_end_time - time.time()) / (self.crossfade_end_time - self.crossfade_start_time)))
            if cf_completion < 0:
                self.is_crossfading = False
                SDL_DestroyTexture(self.old_texture)
                SDL_SetTextureBlendMode(self.texture, SDL_BLENDMODE_NONE)
                SDL_SetTextureBlendMode(self.old_texture, SDL_BLENDMODE_NONE)
            if self.crossfade_type == 'Cross':
                y1 = math.sin((math.pi/255.0)/2*(float(255-cf_completion)))
                y2 = math.sin((math.pi/255.0)/2*(float(255-cf_completion)) + math.pi/2)
                SDL_SetTextureAlphaMod(self.texture, int(255 - y2*255))
                SDL_SetTextureAlphaMod(self.old_texture, int(255 - y1*255))
            elif self.crossfade_type == 'OutIn':
                if (cf_completion >= 128):
                    SDL_SetTextureAlphaMod(self.texture, 0)
                    SDL_SetTextureAlphaMod(self.old_texture, (cf_completion-128)*2)
                else:
                    SDL_SetTextureAlphaMod(self.texture, 255-(cf_completion-128)*2)
                    SDL_SetTextureAlphaMod(self.old_texture, 0)
            elif self.crossfade_type == 'Sine':
                y = math.sin((math.pi/255.0)*float(255-cf_completion))
                if (cf_completion >= 128):
                    SDL_SetTextureAlphaMod(self.texture, 0)
                    SDL_SetTextureAlphaMod(self.old_texture, int(255 - y*255))
                else:
                    SDL_SetTextureAlphaMod(self.texture, int(255 - y*255))
                    SDL_SetTextureAlphaMod(self.old_texture, 0)
        SDL_RenderPresent(self.renderer)

    def setBackgroundColor(self, bkgndColor):
        self.bkgndColor = bkgndColor

    def addObjects(self, objs):
        self.objects.extend(objs)

    def removeObjects(self, objs):
        for o in objs:
            self.removeObject(o)

    def addObject(self, obj):
        self.objects.append(obj)

    def removeObject(self, obj):
        self.objects.remove(obj)


class DrawableObject:
    def __init__(self, dst=None):
        if dst:
            self.dst = dst
        else:
            self.dst = SDL_Rect()
        self.blendmode = SDL_BLENDMODE_NONE
        self.texture = None
        self.visible = True

    def __del__(self):
        if self.texture:
            SDL_DestroyTexture(self.texture)

    def updateDimensions(self):
        w = pointer(c_int(0))
        h = pointer(c_int(0))
        SDL_QueryTexture(self.texture, None, None, w, h)
        self.dst.w = w.contents.value
        self.dst.h = h.contents.value

    def changeLocation(self, dst):
        self.dst = dst

    def changeVisible(self, visible):
        self.visible = visible

    def render(self, renderer):
        if self.visible:
            SDL_SetRenderDrawBlendMode(renderer, self.blendmode)
            sdl2.SDL_RenderCopy(renderer, self.texture, None, self.dst)


class ImageObject(DrawableObject):
    def __init__(self, renderer, imagepath, dst=None):
        DrawableObject.__init__(self, dst=dst)
        self.imagepath = imagepath
        self.texture = loadImageFile(imagepath, renderer)
        DrawableObject.updateDimensions(self)

    def changeImage(self, renderer, imagepath):
        SDL_DestroyTexture(self.texture)
        self.imagepath = imagepath
        self.texture = loadImageFile(imagepath, renderer)
        DrawableObject.updateDimensions(self)


class TextObject(DrawableObject):
    def __init__(self, renderer, string, font, dst=None, color=SDL_Color()):
        DrawableObject.__init__(self, dst=dst)
        self.string = string
        self.font = font
        self.color = color
        self.texture = renderText(self.string, self.font, self.color, renderer)
        DrawableObject.updateDimensions(self)

    def updateTexture(self, renderer):
        if self.texture:
            SDL_DestroyTexture(self.texture)
        self.texture = renderText(self.string, self.font, self.color, renderer)
        DrawableObject.updateDimensions(self)

    def changeFont(self, renderer, font):
        self.font = font
        self.updateTexture(renderer)

    def changeColor(self, renderer, color):
        self.color = color
        self.updateTexture(renderer)

    def changeString(self, renderer, string):
        self.string = string
        self.updateTexture(renderer)
