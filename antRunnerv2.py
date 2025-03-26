import pygame
import sys 

from gpiozero import PWMLED, OutputDevice

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
SPEED = 0.005  # Reduced for smoother animation

class AntennaRunner:
    def __init__(self):
        pygame.init()
        self.font = pygame.font.Font(None, 36)
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()  # Controls frame rate
        self.squirt = 0  # Scaled from 0 to 1
        self.status = "Idle"
        self.PWM = 0  
        self.timeSinceLastTune = 0
        
        #setup the pints for GPIO
        self.pumpDIR = OutputDevice(23)
        self.pumpPWM = PWMLED(12)
        self.ATU = OutputDevice(21)

    @property
    def DIR(self):
        return 0 if self.status == "Retracting" else 1
    @property
    def LEN(self):
        return self.squirt * 20

    @property
    def FREQ(self):
        return 300*(0.25) / self.LEN if self.LEN != 0 else 0

    def scene(self):
        self.screen.fill((0, 0, 0))
        # Fill bar
        pygame.draw.rect(self.screen, BLUE, (75, 50, 25, 500))
        pygame.draw.rect(self.screen, WHITE, (75, 50, 25, 500 * (1 - self.squirt)))

        # Text display
        text1 = self.font.render(f"Approximate Water Length: {self.LEN:.2f} m", True, WHITE)
        text2 = self.font.render(f"Target Frequency: {self.FREQ:.3f} MHz", True, WHITE)
        text3 = self.font.render(f"PWM Duty Cycle: {self.PWM*100:.1f}%", True, WHITE)
        text4 = self.font.render(f"Current Pump Status: {self.status}", True, WHITE)
        text6 = self.font.render(f"Press up arrow to extend", True, WHITE)
        text7 = self.font.render(f"Press down arrow to retract", True, WHITE)
        text8 = self.font.render(f"Press 't' to trigger a tune", True, WHITE)
        
        text9 = self.font.render("0 m", True, WHITE)
        text10 = self.font.render("10 m", True, WHITE)
        text11 = self.font.render("20 m", True, WHITE)

        # Display texts
        self.screen.blit(text1, (300, 100))
        self.screen.blit(text2, (300, 150))
        self.screen.blit(text3, (300, 200))
        self.screen.blit(text4, (300, 300))
        self.screen.blit(text6, (300, 400))
        self.screen.blit(text7, (300, 450))
        self.screen.blit(text8, (300, 500))
        self.screen.blit(text11, (100, 50))
        self.screen.blit(text10, (100, 300))
        self.screen.blit(text9, (100,530))
        pygame.display.flip()

    def run(self):
        while True:
            if self.timeSinceLastTune >= 2000:
                self.ATU.off()
            else:
                self.timeSinceLastTune += 1
            self.scene()  # Render screen
            keys = pygame.key.get_pressed()  # Get key states
            

            if keys[pygame.K_UP]:
                if self.squirt < 1:
                    self.squirt += SPEED
                    self.squirt = min(self.squirt, 1)  # Ensure it doesn't exceed 1
                    self.status = "Extending"
                    self.PWM = 0.5
                    self.pumpPWM.value = self.PWM
                    self.pumpDIR.on()
            elif keys[pygame.K_DOWN]:
                if self.squirt > 0:
                    self.squirt -= SPEED
                    self.squirt = max(self.squirt, 0)  # Ensure it doesn't go below 0
                    self.status = "Retracting"
                    self.PWM = 0.5
                    self.pumpPWM.value = self.PWM
                    self.pumpDIR.off()
            else:
                self.status = "Idle"
                self.PWM = 0  # Stop PWM when no keys are pressed
                self.pumpPWM.value = self.PWM
                self.pumpDIR.on() #better to leave this on in the event that it explodes everything

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_t:
                    # Trigger tune action (if needed)
                    self.ATU.on()
                    self.timeSinceLastTune = 0
                    continue
            
            self.clock.tick(60)  # Limit to 60 FPS for smooth movement

if __name__ == "__main__":
    runner = AntennaRunner()
    runner.run()
