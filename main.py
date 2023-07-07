import discord
import json
import requests, requests.auth
from config import CONFIG

intents = discord.Intents.all()
bot = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(bot)



def get_package(tracking_number = None):

    url = "https://api.ship24.com/public/v1/tracking/search"

    payload = {"trackingNumber": tracking_number}
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Authorization": "apik_DFCEgGNp4UlyuqLNrtWskchOc4fwMT"
        }



    if tracking_number != None:
        package = requests.post(url=url, headers=headers, json=payload)

        return json.loads(package.text)
    
    else:
        return None

@tree.command(name = "locate", description = "Find a package from 1200+ couriers.")
@discord.app_commands.describe(tracking_number="The tracking number for the package to look for.")
async def first_command(interaction, tracking_number: str):

    package_info = get_package(tracking_number)["data"]["trackings"][0]

    print(package_info)

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
                return 0x00ff00
            elif str(package_info["shipment"]["statusMilestone"]) == "info_received":
                return 0x808080
            elif str(package_info["shipment"]["statusMilestone"]) == "in_transit":
                return 0xffff00
            else:
                return 0xff0000
        except:
            return 0xff0000


    Embed = discord.Embed(title=str(package_info["shipment"]["statusCategory"]).title()+": "+tracking_number+" | Status: "+package_info["shipment"]["statusMilestone"].title(), description=description, color=getColor())

    Embed1 = discord.Embed(title="Tracking Information: ", color=0x0000ff)
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
                Tsub = int(TimeSplit[0])-12 
                Prefix = "PM"
            else:
                Tsub = int(TimeSplit[0])
                Prefix = "AM"

            TimeFormat = str(Tsub)+":"+TimeSplit[1]+" "+Prefix


            Embed1.add_field(name=Date, value=">>> "+"**"+TimeFormat+" CDT**"+"\n"+str(event["status"]).title()+"\n"+str(event["location"]).upper(), inline=False)

        except:
            Embed1.add_field(name=Date, value=">>> "+"**"+TimeFormat+" CDT**"+"\n"+str(event["status"]).title()+"\n"+str(event["location"]).upper(), inline=False)

    

    await interaction.channel.send(embed=Embed)
    await interaction.channel.send(embed=Embed1)

@bot.event
async def on_message(msg):
    if "!locate" in msg.content:
        message = str.split(msg.content, " ")
        get_package(tracking_number=message[1])


@bot.event
async def on_ready():
    await tree.sync()
    print("Ready!")

bot.run(CONFIG["TOKEN"])