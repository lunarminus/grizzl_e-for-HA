"""Reboot and Add Schedule buttons for Grizzl-E Connect cloud entries."""
from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import EntityCategory

from .cloud import GrizzleECloudEntity, is_cloud_entry
from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    if not is_cloud_entry(entry) or entry.entry_id not in hass.data.get(DOMAIN, {}):
        return
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([GrizzleERebootButton(coordinator), GrizzleEAddScheduleButton(coordinator)])


class GrizzleERebootButton(GrizzleECloudEntity, ButtonEntity):
    _attr_device_class = ButtonDeviceClass.RESTART
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator):
        super().__init__(coordinator, "reboot", "Reboot")

    async def async_press(self):
        await self.coordinator.async_command(self.coordinator.client.reboot(self.coordinator.station_id))


class GrizzleEAddScheduleButton(GrizzleECloudEntity, ButtonEntity):
    """Create a schedule from the New Schedule name, start, end and day entities."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_icon = "mdi:calendar-plus"

    def __init__(self, coordinator):
        super().__init__(coordinator, "add_schedule", "Add Schedule")

    async def async_press(self):
        draft = self.coordinator.schedule_draft
        name = draft.name.strip()
        if not name:
            raise HomeAssistantError("Enter a name in New Schedule Name first")
        if not draft.days:
            raise HomeAssistantError("Turn on at least one New Schedule day first")
        await self.coordinator.async_command(
            self.coordinator.client.update_schedule(
                self.coordinator.station_id,
                name=name,
                start=(draft.start.hour, draft.start.minute),
                end=(draft.end.hour, draft.end.minute),
                days=sorted(draft.days),
            )
        )
