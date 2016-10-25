import discord
from discord.ext import commands
from .utils import checks
import asyncio
import logging
# Data stuffies
from __main__ import send_cmd_help
from cogs.utils.dataIO import dataIO
import os
import time
import copy
# Tabulate, cause its tabulate
try:
    from tabulate import tabulate
except:
    raise Exception('Run "pip install tabulate" in your CMD/Linux Terminal')
log = logging.getLogger('red.punish')


class Punish:
    """Adds the ability to punish users."""

    # --- Format
    # {
    # Server : {
    #   UserIDs : {
    #       Until :
    #       Givenby :
    #       NumberOfSandwiches :
    #       }
    #    }
    # }
    # ---

    def __init__(self, bot):
        self.bot = bot
        self.location = 'data/punish/settings.json'
        self.json = dataIO.load_json(self.location)
        self.min = ['m', 'min', 'mins', 'minutes', 'minute']
        self.hour = ['h', 'hour', 'hours']
        self.day = ['d', 'day', 'days']
        self.task = bot.loop.create_task(self.check_time())

    def __unload(self):
        self.task.cancel()
        log.debug('Stopped task')

    def _timestamp(self, t, unit):
        if unit in self.min:
            return t * 60 + int(time.time())
        elif unit in self.hour:
            return t * 60 * 60 + int(time.time())
        elif unit in self.day:
            return t * 60 * 60 * 24 + int(time.time())
        else:
            raise Exception('Invalid Unit')

    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def punish(self, ctx, user: discord.Member, t: int=1, unit='hour'):
        """Places a user in timeout for a period of time.

        Valid unit of times are minutes, hours & days.
        Example usage: !punish @Kowlin 3 hours"""
        server = ctx.message.server
        # --- CREATING ROLE ---
        if 'Punished' not in [r.name for r in server.roles]:
            await self.bot.say('The Punished role doesn\'t exist! Creating it now!')
            log.debug('Creating Punished role in {}'.format(server.id))
            try:
                perms = discord.Permissions.none()
                await self.bot.create_role(server, name='Punished', permissions=perms)
                await self.bot.say("Role created! Setting channel permissions!\nPlease ensure that your moderator roles are ABOVE the Punished role!\nPlease wait until the user has been added to the Timeout role!")
                try:
                    r = discord.utils.get(server.roles, name='Punished')
                    perms = discord.PermissionOverwrite()
                    perms.send_messages = False
                    for c in server.channels:
                        if c.type.name == 'text':
                            await self.bot.edit_channel_permissions(c, r, perms)
                            await asyncio.sleep(1.5)
                except discord.Forbidden:
                    await self.bot.say("A error occured while making channel permissions.\nPlease check your channel permissions for the Punished role!")
            except discord.Forbidden:
                await self.bot.say("I cannot create a role. Please assign Manage Roles to me!")
        role = discord.utils.get(server.roles, name='Punished')
        # --- DONE CREATING ROLE! ---
        # --- JSON SERVER LOGIC ---
        if server.id not in self.json:
            log.debug('Adding server({}) in Json'.format(server.id))
            self.json[server.id] = {}
            dataIO.save_json(self.location, self.json)
        # --- DONE JSON SERVER LOGIC! ---
        # --- ASSIGNING TIMESTAMPS AND ROLE ---
        try:
            if user.id == ctx.message.author.id:
                await self.bot.say('Please don\'t punish yourself :(')
            elif user.id not in self.json[server.id] and role not in user.roles:
                # USER NOT IN PUNISH, NO ROLE
                until = self._timestamp(t, unit)
                self.json[server.id][user.id] = {'until': until, 'givenby': ctx.message.author.id}
                dataIO.save_json(self.location, self.json)
                await self.bot.add_roles(user, role)
                await self.bot.say('``{}`` is now Punished for {} {} by ``{}``.'.format(user.display_name, str(t), unit, ctx.message.author.display_name))
            elif user.id in self.json[server.id] and role not in user.roles:
                # USER IN PUNISH, NO ROLE
                    await self.bot.add_roles(user, role)
                    await self.bot.say('Role reapplied on {}'.format(user.display_name))
            elif user.id not in self.json[server.id] and role in user.roles:
                # USER NOT IN PUNISH, HAS ROLE
                until = self._timestamp(t, unit)
                self.json[server.id][user.id] = {'until': until, 'givenby': ctx.message.author.id}
                dataIO.save_json(self.location, self.json)
                await self.bot.say('``{}`` is now Punished for {} {} by ``{}``.'.format(user.display_name, str(t), unit, ctx.message.author.display_name))
            else:
                # USER IN PUNISH, HAS ROLE
                await self.bot.say('``{}`` is already punished. Please use ``unpunish`` to unpunish the user.'.format(user.display_name))
        except:
            await self.bot.say('Invalid unit')

    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def unpunish(self, ctx, user: discord.Member):
        """Unpunishes a punished user"""
        if user.id in self.json[ctx.message.server.id]:
            r = discord.utils.get(ctx.message.server.roles, name='Punished')
            del self.json[ctx.message.server.id][user.id]
            await self.bot.remove_roles(user, r)
            dataIO.save_json(self.location, self.json)
            await self.bot.say('``{}`` is now unpunished.'.format(user.display_name))

    @commands.command(pass_context=True, no_pm=True)
    async def muted(self, ctx):
        """Shows the list of punished users"""
        # Populate a list with other lists, they act as tables
        server = ctx.message.server
        table = []
        if server.id in self.json:
            for user in self.json[server.id]:
                temp = []
                # Get the user display_name
                user_obj = discord.utils.get(server.members, id=user)
                log.debug(user_obj)
                if user_obj is None:
                    temp.append('ID: {}'.format(user))
                else:
                    temp.append(user_obj.display_name)
                    # Get the time in minutes or hours, (hopefully)
                    remaining = self.json[server.id][user]['until'] - int(time.time())
                if remaining < 60:
                    temp.append('<1 Minute')
                elif remaining < 120:
                    temp.append('1 Minute')
                elif remaining < 3600:
                    remaining = remaining / 60
                    temp.append('{} Minutes'.format(int(remaining)))
                elif remaining < 86400:
                    remaining = remaining / 60 / 60
                    temp.append('{} Hours'.format(int(remaining)))
                else:
                    remaining = remaining / 60 / 60 / 24
                    temp.append('{} Days'.format(int(remaining)))
                # Get the givenby
                given_obj = discord.utils.get(server.members, id=self.json[server.id][user]['givenby'])
                if given_obj is None:
                    temp.append('ID: {}'.format(self.json[server.id][user]['givenby']))
                else:
                    temp.append(given_obj.display_name)
                    table.append(temp)
            header = ['Member', 'Time Remaining', 'Given By']
            await self.bot.say('```\n{}```'.format(tabulate(table, headers=header, tablefmt='simple')))
        else:
            await self.bot.say('No punishments are given out on this server.')

    # Look for new channels, and slap the role in there face!
    async def new_channel(self, c):
        if 'Punished' in [r.name for r in c.server.roles]:
            if c.type.name == 'text':
                perms = discord.PermissionOverwrite()
                perms.send_messages = False
                r = discord.utils.get(c.server.roles, name='Punished')
                await self.bot.edit_channel_permissions(c, r, perms)
                log.debug('Punished role created on channel: {}'.format(c.id))

    async def check_time(self):
        while True:
            await asyncio.sleep(30)
            json = copy.deepcopy(self.json)
            log.debug('First Timer')
            for server in json:
                server_obj = discord.utils.get(self.bot.servers, id=server)
                role_obj = discord.utils.get(server_obj.roles, name='Punished')
                log.debug('Server Object = {}'.format(server_obj))
                for user in json[server]:
                    user_obj = discord.utils.get(server_obj.members, id=user)
                    log.debug('User Object = {}'.format(user_obj))
                    if json[server][user]['until'] < int(time.time()):
                        log.debug('Expired user ({})'.format(user))
                        await self.bot.remove_roles(user_obj, role_obj)
                        del self.json[server][user]
                        dataIO.save_json(self.location, self.json)
            log.debug('after loops')

    async def new_member(self, member):
        if member.server.id in self.json:
            if member.id in self.json[member.server.id]:
                r = discord.utils.get(member.server.roles, name='Punished')
                await self.bot.add_roles(member, r)
                log.debug('User ({}) joined while punished.'.format(member.id))


def check_folder():
    if not os.path.exists('data/punish'):
        log.debug('Creating folder: data/punish')
        os.makedirs('data/punish')


def check_file():
    f = 'data/punish/settings.json'
    if dataIO.is_valid_json(f) is False:
        log.debug('Creating json: settings.json')
        dataIO.save_json(f, {})


def setup(bot):
    check_folder()
    check_file()
    n = Punish(bot)
    bot.add_cog(n)
    bot.add_listener(n.new_member, 'on_member_join')
    bot.add_listener(n.new_channel, 'on_channel_create')
