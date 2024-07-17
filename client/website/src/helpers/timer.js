import { useState, useEffect } from 'react';

function useMinuteTick() {
    const [currentMinute, setCurrentMinute] = useState(new Date().getMinutes());

    useEffect(() => {
        const intervalId = setInterval(() => {
            const newMinute = new Date().getMinutes();
            if (newMinute !== currentMinute) {
                setCurrentMinute(newMinute);
            }
        }, 50);

        // Cleanup interval on component unmount
        return () => clearInterval(intervalId);
    }, [currentMinute]);

    return currentMinute;
}

export default useMinuteTick;