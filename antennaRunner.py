import pygame
import sys

from gpiozero import PWMLED, OutputDevice #a couple of recipies for pins from gpiozero

# Define the pins for the PWM and the relay
#Hi/Lo control for the pump is on pin 16 GPIO23
#the PWM is on pin 32 GPIO12
#the relay for the ATU is on pin 40 GPIO21



class AntennaRunner:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.font = pygame.font.Font(None, 36)
        self.state = "START/RESET"
        self.progress = 0
        self.calibration_duration = 20000  # Calibration duration in milliseconds
        self.start_time = None
        self.input_text = ""
        self.input_box = pygame.Rect(100, 150, 140, 50)
        self.input_active = False

        # variables relating to antenna status
        self.PWM = 0
        self.BAND = 20
        self.frequency = 7.2

        #setup the pins for GPIO
        self.pumpDIR = OutputDevice(23) #instantiate the pin using the GPIO number, not the physical pin number
        self.pumpPWM = PWMLED(12) #just pretend it's an LED, should be sufficient to drive the H-Bridge
        self.ATU = OutputDevice(21)

        #set the pump dir to high (3.3)
        self.pumpDIR.on()


    @property
    def LEN(self):
        return self.BAND/2

    
    def computeTargetBand(self, frequency):
        target_wavelength = 300 / frequency
        band_targets = [10,20,30,40,80,100]
        differences = [abs(target_wavelength - band) for band in band_targets]
        closest_band = band_targets[differences.index(min(differences))]
        return closest_band
    
    def bandToPumpPWM(self, band):
        #should vary from .1 to .9 accross 6 increments
        params = {
            10: 0.1,
            20: 0.3,
            30: 0.5,
            40: 0.7,
            80: 0.8,
            100: 0.9
        }
        return params[band]

    


    def start_reset(self):
        self.screen.fill((0, 0, 0))
        text = self.font.render("Input Frequency (3-30MHz)", True, (255, 255, 255))
        self.screen.blit(text, (50, 100))
        text = self.font.render("Enter to confirm...", True, (255, 255, 255))
        self.screen.blit(text, (310, 170))

        # Draw the input box
        pygame.draw.rect(self.screen, (255, 255, 255), self.input_box, 2)
        input_text_surface = self.font.render(self.input_text, True, (255, 255, 255))
        self.screen.blit(input_text_surface, (self.input_box.x + 5, self.input_box.y + 5))
        self.input_box.w = max(200, input_text_surface.get_width() + 10)

        pygame.draw.rect(self.screen, (0, 255, 0), (100, 300, 250, 50))
        text = self.font.render("Begin Calibration", True, (255, 255, 255))
        self.screen.blit(text, (100, 300))

        #on the right side of the screen display what the frequency is going to be
        text = self.font.render(f"Frequency: {self.frequency} MHz", True, (255, 255, 255))
        self.screen.blit(text, (400, 300))
        pygame.display.flip()

    def calibrate(self):
        if self.start_time is None:
            self.start_time = pygame.time.get_ticks()

        #text box saying what band we are tuning to 
        text = self.font.render(f"Tuning to {self.BAND} meters", True, (255, 255, 255))

        #if the progress is 75% or more, then show a text box indicating that we are triggering the ATU
        if self.progress >= 0.75:
            text = self.font.render("Triggering ATU. Send tune signal", True, (255, 255, 255))
            self.screen.blit(text, (50, 400))



        elapsed_time = pygame.time.get_ticks() - self.start_time
        self.progress = min(elapsed_time / self.calibration_duration, 1)

        self.screen.fill((0, 0, 0))
        pygame.draw.rect(self.screen, (255, 255, 255), (100, 200, 600, 50))
        pygame.draw.rect(self.screen, (0, 255, 0), (100, 200, 600 * self.progress, 50))
        self.screen.blit(text, (100, 300))
        pygame.display.flip()

        if elapsed_time >= self.calibration_duration:
            self.state = "STATUS"
            self.start_time = None

    def status(self):
        self.screen.fill((0, 0, 0))
        text = self.font.render(f"PWM: {self.PWM*100}%", True, (255, 255, 255))
        self.screen.blit(text, (100, 200))
        text = self.font.render(f"Band: {self.BAND} meters", True, (255, 255, 255))
        self.screen.blit(text, (100, 300))
        text = self.font.render(f"Length: {self.LEN} meters", True, (255, 255, 255))
        self.screen.blit(text, (100, 400))
        pygame.draw.rect(self.screen, (255, 0, 0), (100, 500, 200, 50))
        text = self.font.render("Reset", True, (255, 255, 255))
        self.screen.blit(text, (100, 500))
        pygame.display.flip()

    def run(self):
        while True:
            if self.state == "START/RESET":
                self.start_reset()
            elif self.state == "CALIBRATE":
                #turn on the pump by setting the PWM to the correct value
                self.pumpPWM.value = self.PWM
                self.calibrate()
            elif self.state == "STATUS":
                self.status()
            #if 15 seconds have elapsed then trigger the ATU if it's not already triggered
            if self.progress >= 0.75 and self.ATU.value == 0:
                self.ATU.on()


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    #clean up the pins
                    self.pumpPWM.close()
                    self.pumpDIR.close()
                    self.ATU.close()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == "START/RESET":
                        if self.input_box.collidepoint(event.pos):
                            self.input_active = True
                        else:
                            self.input_active = False
                        if 100 <= event.pos[0] <= 300 and 300 <= event.pos[1] <= 350:
                            #compute stuff and move to the next state
                            self.BAND = self.computeTargetBand(self.frequency)
                            self.PWM = self.bandToPumpPWM(self.BAND)
                            self.state = "CALIBRATE"
                    elif self.state == "STATUS":
                        if 100 <= event.pos[0] <= 300 and 500 <= event.pos[1] <= 550:
                            self.state = "START/RESET"
                if event.type == pygame.KEYDOWN:
                    if self.input_active:
                        if event.key == pygame.K_RETURN:
                            if float(self.input_text) < 3 or float(self.input_text) > 30: #make sure that the frequency is in HF
                                self.input_text = ""
                            self.frequency = float(self.input_text)
                            self.input_text = ""
                        elif event.key == pygame.K_BACKSPACE:
                            self.input_text = self.input_text[:-1]
                        else:
                            #check that the input is a number or .
                            if event.unicode.isnumeric() or event.unicode == ".":
                                self.input_text += event.unicode


if __name__ == "__main__":
    runner = AntennaRunner()
    runner.run()
