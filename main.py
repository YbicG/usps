import discord
import json
import time
import threading
import track
import requests, requests.auth
from config import CONFIG

class thread(threading.Thread):
    def __init__(self, thread_name, thread_ID):
        threading.Thread.__init__(self)
        self.thread_name = thread_name
        self.thread_ID = thread_ID
 
        # helper function to execute the threads
    def run(self):
        if self.thread_name == "Tracking":
        	track.run()

Bot2 = thread("Tracking", 2)
Bot2.start()


intents = discord.Intents.all()
bot = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(bot)

# Class of different styles
class style():
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    NONE = '\033[0m'

def get_package(tracking_number=" "):
    tracking_number = tracking_number.replace(" ", "")

    url = "https://api.ship24.com/public/v1/tracking/search"

    payload = {"trackingNumber": tracking_number}
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Authorization": "apik_O6Y0Ybjz5kkXBajM9MGepQKhCxhI5p",
    }

    if tracking_number != " " and tracking_number != None:
        package = requests.post(url=url, headers=headers, json=payload)

        if "errors" in json.loads(package.text):
            print(f"{style.RED}[ERROR]{style.NONE} {style.MAGENTA} Tracking Number: "+str(tracking_number)+f"{style.NONE} {style.YELLOW}"+json.loads(package.text)["errors"][0]["message"]+style.NONE)
            return False, {}
        elif json.loads(package.text)["data"]["trackings"][0]["shipment"]["shipmentId"] is None:
            return False, {}
        else:
            return True, json.loads(package.text)

    else:
        return False, {}


@tree.command(name="locate", description="Find a package from 1200+ couriers.")
@discord.app_commands.describe(
    tracking_number_list="The tracking numbers for the package to look for (separated by commas)."
)
async def first_command(interaction, tracking_number_list: str):
    
    await interaction.response.send_message(content="‎")

    current_index = 0

    if "," in tracking_number_list:
        tracking_numbers = tracking_number_list.split(",")

        for index in range(len(tracking_numbers)):

            current_index = index

            tracking_number = tracking_numbers[index]

            if len(tracking_number) >= 2:
                isValid, package_info = get_package(tracking_number)

                if isValid:
                    package_info = package_info["data"]["trackings"][0]

                    description = f"""
                    
                    **Estimated Delivery Date:** {str(package_info["shipment"]["delivery"]["estimatedDeliveryDate"])}

                    **Recipient:**
                        > *Name:* {str(package_info["shipment"]["recipient"]["name"])}
                        > *Address:* {str(package_info["shipment"]["recipient"]["address"])}
                        > *Postal Code:* {str(package_info["shipment"]["recipient"]["postCode"])}
                        > *City:* {str(package_info["shipment"]["recipient"]["city"])}
                        > *State/Region:* {str(package_info["shipment"]["recipient"]["subdivision"])}

                    **Service:** {str(package_info["shipment"]["delivery"]["service"])}
                    """

                    try:
                        footer = f"{str(package_info['events'][0]['sourceCode'])} | {str(package_info['shipment']['shipmentId'])}".upper()
                    except:
                        footer = "No Info".upper()
                        pass

                    def getColor():
                        try:
                            if (
                                str(package_info["shipment"]["statusMilestone"])
                                == "delivered"
                            ):
                                return 0x00FF00
                            elif (
                                str(package_info["shipment"]["statusMilestone"])
                                == "info_received"
                            ):
                                return 0x808080
                            elif (
                                str(package_info["shipment"]["statusMilestone"])
                                == "in_transit"
                            ):
                                return 0xFFFF00
                            else:
                                return 0xFF0000
                        except:
                            return 0xFF0000

                    Embed = discord.Embed(
                        title=str(package_info["shipment"]["statusCategory"]).title()
                        + ": "
                        + tracking_number
                        + " | Status: "
                        + package_info["shipment"]["statusMilestone"].title(),
                        description=description,
                        color=getColor(),
                    )

                    Embed1 = discord.Embed(
                        title="Tracking Information: ", color=0x0000FF
                    )
                    Embed1.set_footer(text=footer)

                    for event in package_info["events"]:
                        DT = str(event["occurrenceDatetime"])
                        TimeFormat = DT

                        try:
                            DT = DT.split("T")
                            Date = DT[0]
                            Time = DT[1]

                            TimeSplit = Time.split(":")

                            if int(TimeSplit[0]) > 12:
                                Tsub = int(TimeSplit[0]) - 12
                                Prefix = "PM"
                            else:
                                Tsub = int(TimeSplit[0])
                                Prefix = "AM"

                            TimeFormat = str(Tsub) + ":" + TimeSplit[1] + " " + Prefix

                            Embed1.add_field(
                                name=Date,
                                value=">>> "
                                + "**"
                                + TimeFormat
                                + " CDT**"
                                + "\n"
                                + str(event["status"]).title()
                                + "\n"
                                + str(event["location"]).upper(),
                                inline=False,
                            )

                        except:
                            Embed1.add_field(
                                name=Date,
                                value=">>> "
                                + "**"
                                + TimeFormat
                                + " CDT**"
                                + "\n"
                                + str(event["status"]).title()
                                + "\n"
                                + str(event["location"]).upper(),
                                inline=False,
                            )

                    embedFinal = discord.Embed(color=0xffffff, title="Tracker Number #"+str(index+1), description="<:line:1112022903760879667><:line:1112022903760879667><:line:1112022903760879667><:line:1112022903760879667><:line:1112022903760879667><:line:1112022903760879667><:line:1112022903760879667><:line:1112022903760879667><:line:1112022903760879667><:line:1112022903760879667><:line:1112022903760879667><:line:1112022903760879667><:line:1112022903760879667><:line:1112022903760879667><:line:1112022903760879667><:line:1112022903760879667><:line:1112022903760879667><:line:1112022903760879667><:line:1112022903760879667><:line:1112022903760879667>")
                    await interaction.channel.send(content="‎\n", embed=embedFinal)
                    await interaction.channel.send(embed=Embed)
                    await interaction.channel.send(embed=Embed1)

                else:
                    Embed = discord.Embed(
                        title="Not Existent: " + tracking_number + " | Status: Invalid",
                        description="Invalid Shipment Code",
                        color=0xFF0000,
                    )
                    embedFinal = discord.Embed(color=0xffffff, title="Tracker Number #"+str(current_index+1), description="<:line:1112022903760879667><:line:1112022903760879667><:line:1112022903760879667><:line:1112022903760879667><:line:1112022903760879667><:line:1112022903760879667><:line:1112022903760879667><:line:1112022903760879667><:line:1112022903760879667><:line:1112022903760879667><:line:1112022903760879667><:line:1112022903760879667><:line:1112022903760879667><:line:1112022903760879667><:line:1112022903760879667><:line:1112022903760879667><:line:1112022903760879667><:line:1112022903760879667><:line:1112022903760879667><:line:1112022903760879667>")
                    await interaction.channel.send(content="‎\n", embed=embedFinal)
                    await interaction.channel.send(embed=Embed)

    else:

        tracking_number = tracking_number_list
        isValid, package_info = get_package(tracking_number)

        if isValid:
            package_info = package_info["data"]["trackings"][0]

            description = f"""
                    
                    **Estimated Delivery Date:** {str(package_info["shipment"]["delivery"]["estimatedDeliveryDate"])}

                    **Recipient:**
                        > *Name:* {str(package_info["shipment"]["recipient"]["name"])}
                        > *Address:* {str(package_info["shipment"]["recipient"]["address"])}
                        > *Postal Code:* {str(package_info["shipment"]["recipient"]["postCode"])}
                        > *City:* {str(package_info["shipment"]["recipient"]["city"])}
                        > *State/Region:* {str(package_info["shipment"]["recipient"]["subdivision"])}

                    **Service:** {str(package_info["shipment"]["delivery"]["service"])}
                    """

            try:
                footer = f"{str(package_info['events'][0]['sourceCode'])} | {str(package_info['shipment']['shipmentId'])}".upper()
            except:
                footer = "No Info".upper()
                pass

            def getColor():
                try:
                    if str(package_info["shipment"]["statusMilestone"]) == "delivered":
                        return 0x00FF00
                    elif (
                        str(package_info["shipment"]["statusMilestone"])
                        == "info_received"
                    ):
                        return 0x808080
                    elif (
                        str(package_info["shipment"]["statusMilestone"]) == "in_transit"
                    ):
                        return 0xFFFF00
                    else:
                        return 0xFF0000
                except:
                    return 0xFF0000

            Embed = discord.Embed(
                title=str(package_info["shipment"]["statusCategory"]).title()
                + ": "
                + tracking_number
                + " | Status: "
                + package_info["shipment"]["statusMilestone"].title(),
                description=description,
                color=getColor(),
            )

            Embed1 = discord.Embed(title="Tracking Information: ", color=0x0000FF)
            Embed1.set_footer(text=footer)

            for event in package_info["events"]:
                DT = str(event["occurrenceDatetime"])
                TimeFormat = DT

                try:
                    DT = DT.split("T")
                    Date = DT[0]
                    Time = DT[1]

                    TimeSplit = Time.split(":")

                    if int(TimeSplit[0]) > 12:
                        Tsub = int(TimeSplit[0]) - 12
                        Prefix = "PM"
                    else:
                        Tsub = int(TimeSplit[0])
                        Prefix = "AM"

                    TimeFormat = str(Tsub) + ":" + TimeSplit[1] + " " + Prefix

                    Embed1.add_field(
                        name=Date,
                        value=">>> "
                        + "**"
                        + TimeFormat
                        + " CDT**"
                        + "\n"
                        + str(event["status"]).title()
                        + "\n"
                        + str(event["location"]).upper(),
                        inline=False,
                    )

                except:
                    Embed1.add_field(
                        name=Date,
                        value=">>> "
                        + "**"
                        + TimeFormat
                        + " CDT**"
                        + "\n"
                        + str(event["status"]).title()
                        + "\n"
                        + str(event["location"]).upper(),
                        inline=False,
                    )

            await interaction.channel.send(embed=Embed)
            await interaction.channel.send(embed=Embed1)

        else:
            Embed = discord.Embed(
                title="Tracking Number: " + tracking_number + " | Status: Invalid",
                description="Invalid Shipment Code",
                color=0xFF0000,
            )
            await interaction.channel.send(embed=Embed)

"""

@bot.event
async def on_message(msg):
    if "!locate" in msg.content:
        message = str.split(msg.content, " ")
        get_package(tracking_number=message[1])

"""


@bot.event
async def on_ready():
    print("Ready!")
    await tree.sync()


bot.run(CONFIG["TOKEN"])
