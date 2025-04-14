import * as React from "react";

interface LabelProps extends React.LabelHTMLAttributes<HTMLLabelElement> {
    htmlFor?: string;
}

const Label = React.forwardRef<HTMLLabelElement, LabelProps>(({ className, htmlFor, ...props }, ref) => {
    return (
        <label
            ref={ref}
            htmlFor={htmlFor}
            className={`text-sm font-medium leading-none ${className || ""}`}
            {...props}
        />
    );
});

Label.displayName = "Label";

export { Label };
