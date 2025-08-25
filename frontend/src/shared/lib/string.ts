export const capitalize = (s: string) => {
	if (s.length === 0) return s;
	return s.charAt(0).toUpperCase() + s.slice(1);
};

export const getInitials = (name: string) => {
	const names = name.split(" ");
	let initials = names[0].charAt(0).toUpperCase();
	if (names.length > 1) {
		initials += names[names.length - 1].charAt(0).toUpperCase();
	}
	return initials;
};
