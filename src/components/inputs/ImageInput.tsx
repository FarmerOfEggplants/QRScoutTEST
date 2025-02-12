import { inputSelector, updateValue, useQRScoutState } from "@/store/store";
import { ImageInputData } from './BaseInputProps';
import { ConfigurableInputProps } from "./ConfigurableInput";
import { useCallback, useEffect, useState } from "react";
import { useEvent } from "@/hooks/useEvent";

// type coordinatePoint = [number, number];

export default function(props: ConfigurableInputProps) {
    const data = useQRScoutState(
        inputSelector<ImageInputData>(props.section, props.code),
    );

    if (!data) {
        return <div>Invalid input</div>;
      }

    const [value, setValue] = useState(data.defaultValue);

    const resetState = useCallback(
        ({ force }: { force: boolean }) => {
            console.log(
              `resetState ${data.code}`,
              `force: ${force}`,
                `behavior: ${data.formResetBehavior}`,
            );
            if (force) {
              setValue(data.defaultValue);
                return;
            }
            switch (data.formResetBehavior) {
            case 'reset':
                setValue(data.defaultValue);
                return;              
            case 'preserve':
                return;
            default:
                return;
            }
        },
    [data.defaultValue, value],
    );
    
    useEvent('resetFields', resetState);
    
    useEffect(() => {
        updateValue(props.code, value);
      }, [value]);
} 